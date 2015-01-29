#! /usr/bin/perl 
#
# http://www.cfht.hawaii.edu/~chyan/wircam/badpix/badpix.html
#----------------------------------------------------------------------------
#                             wircampolyregion
#----------------------------------------------------------------------------
# Contents: This script parse the ds9 region file into better format.  The out
#                out file can be easily used for IDL program.
#----------------------------------------------------------------------------
# Part of:     WIRcam C pipeline                               
# From:        ASIAA                    
# Author:      Chi-hung Yan(chyan@asiaa.sinica.edu.tw)                       
#----------------------------------------------------------------------------

use warnings;
use strict;

# Define global variable
our $SCRIPT_NAME = 'wircampolyregion';

sub trim {
   my $string=$_;
   for ($string) {
       s/^\s+//;
       s/\s+$//;
    }
   return $string;
}

# This finction is used to return program usage.
sub usage(){

print<<EOF
 USAGE: $SCRIPT_NAME <ds9.reg> <output.txt>


 EXAMPLES:
  $SCRIPT_NAME ds9.reg output.txt

EOF
}

if(@ARGV == 0 || @ARGV != 2){
   usage();
   exit 0;
}

my $file = $ARGV[0];
my $i=0;
my $j=0;
my $ext;
my $reg=0;

open(OUT,">$ARGV[1]");
open(FILE,$file);
while(<FILE>){
    if (/^# tile/){
        my @chip=split(" ",$_);
        $ext = $chip[2];
    }
    if (/^polygon/){
        $reg=$reg+1;
        my @word=split(/[\(\)]/,$_);
        my @coord=split(",",$word[1]);
        my $n=@coord/2;
        for ($i=0;$i<$n;$i++){
            printf(OUT "%d %d %7.2f %7.2f\n",$reg,$ext,$coord[2*$i],$coord[2*$i+1]);
        }    
    }
    if (/^box/){
        $reg=$reg+1;
        my @word=split(/[\(\)]/,$_);
        my @para=split(",",$word[1]);
        printf("$word[1]\n");
         printf(OUT "%d %d %7.2f %7.2f\n",$reg,$ext,$para[0]-$para[2]/2,$para[1]-$para[3]/2);
         printf(OUT "%d %d %7.2f %7.2f\n",$reg,$ext,$para[0]+$para[2]/2,$para[1]-$para[3]/2);
         printf(OUT "%d %d %7.2f %7.2f\n",$reg,$ext,$para[0]+$para[2]/2,$para[1]+$para[3]/2);
         printf(OUT "%d %d %7.2f %7.2f\n",$reg,$ext,$para[0]-$para[2]/2,$para[1]+$para[3]/2);
    }    


}

close(OUT);