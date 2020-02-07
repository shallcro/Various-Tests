#!/usr/bin/env perl

# Copyright (c) 2014 Nicolas George
#
# This file is part of FFmpeg.
#
# FFmpeg is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# FFmpeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with FFmpeg; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

=head1 NAME
dvd2concat - create a concat script for a DVD title
=head1 SYNOPSIS
tools/dvd2concat I<path/to/dvd/structure> > I<file.concat>
=head1 DESCRIPTION
This script uses B<lsdvd> to produce concat script for a DVD title.
The resulting script can be used to play the DVD using B<ffplay>, to
transcode it using B<ffmpeg> or any other similar use.
I<path/to/dvd/structure> is the path to the DVD structure hierarchy; it
normally contains a directory named B<VIDEO_TS>. It must not be encrypted
with CSS.
I<file.concat> is the output file. It can be used as an input to ffmpeg.
It will require the B<-safe 0> option.
=cut

use strict;
use warnings;
use Getopt::Long ":config" => "require_order";
use Pod::Usage;

my $title;

GetOptions (
  "help|usage|?|h" => sub { pod2usage({ -verbose => 1, -exitval => 0 }) },
  "manpage|m"      => sub { pod2usage({ -verbose => 2, -exitval => 0 }) },
  "title|t=i"      => \$title,
) and @ARGV == 1 or pod2usage({ -verbose => 1, -exitval => 1 });
my ($path) = @ARGV;

my $lsdvd_message =
"Make sure your lsdvd version has the two following patches applied:\n" .
"http://sourceforge.net/p/lsdvd/feature-requests/1/\n" .
"https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=603826\n";

my $lsdvd = do {
  open my $l, "-|", "lsdvd", "-Op", "-x", $path
    or die "You need to install lsdvd for this script to work.\n$lsdvd_message";
  local $/;
  <$l>;
};
my %lsdvd = eval $lsdvd;
die $@ if $@;

if (!defined $title) {
  $title = $lsdvd{longest_track};
  warn "Using longest title $title\n";
}
my $track = $lsdvd{track}[$title - 1]
  or die "Title $title does not exist (1-", scalar(@{$lsdvd{track}}), ")\n";
my $vts_base = sprintf "%s/VIDEO_TS/VTS_%02d_", $path, $track->{vts};
my @frag;
for my $i (1 .. 9) {
  my $file = sprintf "%s%d.VOB", $vts_base, $i;
  my $size = -s $file or last;
  push @frag, { file => $file, size => $size >> 11 };
}

my $concat = "ffconcat version 1.0\n";
$concat .= "\nstream\nexact_stream_id 0x1E0\n";
for my $audio (@{$track->{audio}}) {
  $concat .= "\nstream\nexact_stream_id " . $audio->{streamid} . "\n";
}
for my $subp (@{$track->{subp}}) {
  $concat .= "\nstream\nexact_stream_id " . $subp->{streamid} . "\n";
}
for my $cell (@{$track->{cell}}) {
  my $off = $cell->{first_sector};
  die "Your lsdvd version does not print cell sectors.\n$lsdvd_message"
    unless defined $off;
  my $size = $cell->{last_sector} + 1 - $cell->{first_sector};

  my $frag = 0;
  while ($frag < @frag) {
    last if $off < $frag[$frag]->{size};
    $off -= $frag[$frag++]->{size};
  }
  die "Cell beyond VOB data\n" unless $frag < @frag;
  my $cur_off = $off;
  my $cur_size = $size;
  my @files;
  while ($cur_size > $frag[$frag]->{size} - $cur_off) {
    push @files, $frag[$frag]->{file};
    $cur_size -= $frag[$frag]->{size} - $cur_off;
    $cur_off = 0;
    die "Cell end beyond VOB data\n" unless ++$frag < @frag;
  }
  push @files, $frag[$frag]->{file};
  my $file = @files == 1 ? $files[0] : "concat:" . join("|", @files);
  my $start = $off << 11;
  my $end = ($off + $size) << 11;
  $file = "subfile,,start,${start},end,${end},,:$file";

  my $dur = int(1000 * $cell->{length});
  $concat .= sprintf "\nfile '%s'\nduration %02d:%02d:%02d.%03d\n", $file,
    int($dur / 3600000), int($dur / 60000) % 60, int($dur / 1000) % 60,
    $dur % 1000;
}

print $concat;