#!/usr/bin/perl

# queries Factory Jenkins JSON api to find latest good 
# android build of master or stable branch.
#  
#  Call with these parameters:
#  
#  BRANCH          e.g. master, 2.5.0
#  
use warnings;
#use strict;
$|++;

use File::Basename;
use Cwd qw(abs_path);
BEGIN
    {
    $THIS_DIR = dirname( abs_path($0));    unshift( @INC, $THIS_DIR );
    }
my $installed_URL='http://factory.hq.couchbase.com/cgi/show_latest_and.cgi';

use jenkinsQuery     qw(:DEFAULT );
use jenkinsReports   qw(:DEFAULT );
use buildbotReports  qw(:DEFAULT );

use CGI qw(:standard);
my  $query = new CGI;

my $DEBUG = 0;

my $delay = 2 + int rand(5.3);    sleep $delay;

my ($good_color, $warn_color, $err_color, $note_color) = ('#CCFFDD', '#FFFFCC', '#FFAAAA', '#CCFFFF');

my %release = ( 'master' => '0.0',
                'stable' => '1.0',
              );
my $builder;

my $timestamp = "";
sub get_timestamp
    {
    my $timestamp;
    my ($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
    my @months = qw(Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec);
    $month =    1 + $month;
    $year  = 1900 + $yearOffset;
    $timestamp = "page generated $hour:$minute:$second  on $year-$month-$dayOfMonth";
    }

sub print_HTML_Page
    {
    my ($frag_left, $frag_right, $page_title, $color) = @_;
    
    print $query->header;
    print $query->start_html( -title   => $page_title,
                              -BGCOLOR => $color,
                            );
    print "\n".'<div style="overflow-x: hidden">'."\n"
         .'<table border="0" cellpadding="0" cellspacing="0"><tr>'."\n".'<td valign="TOP">'.$frag_left.'</td><td valign="TOP">'.$frag_right.'</td></tr>'."\n".'</table>'
         .'</div>'."\n";
    print $query->end_html;
    }

my $usage = "ERROR: must specify 'branch' and 'outcome'\n\n"
           ."<PRE>"
           ."For example:\n\n"
           ."    $installed_URL?branch=master&outcome=good\n"
           ."    $installed_URL?branch=stable&outcome=done\n"
           ."</PRE><BR>"
           ."\n"
           ."\n";

my ($platform, $branch, $job_type);

if ( $query->param('branch') && $query->param('outcome') )
    {
    $branch   = $query->param('branch');
    $outcome  = $query->param('outcome');
    $builder  = jenkinsReports::get_builder($platform, $branch, 'build', 'and');
    if ($DEBUG)  { print STDERR "\nready to start with ($builder, $branch)\n"; }
    }
else
    {
    print_HTML_Page( buildbotQuery::html_ERROR_msg($usage), '&nbsp;', $builder, $err_color );
    exit;
    }
my ($bldstatus, $bldnum, $rev_numb, $bld_date, $is_running);


#### S T A R T  H E R E 

if ($outcome =~ 'good')
    {
    ($bldnum, $is_running, $bld_date, $bldstatus) = jenkinsReports::last_good_and_bld($platform, $branch);
    }
if ($outcome =~ 'done')
    {
    ($bldnum, $is_running, $bld_date, $bldstatus) = jenkinsReports::last_done_and_bld($platform, $branch);
    }
$rev_numb = $release{$branch}.'-'.$bldnum;

if ($DEBUG)  { print STDERR "according to last_done_build, is_running = $is_running\n"; }

if ($bldnum < 0)
    {
    if ($DEBUG)  { print STDERR "blndum < 0, no build yet\n"; }
    print_HTML_Page( $bld_date,
                     buildbotReports::is_running($is_running),
                     $builder,
                     $note_color );
    }
elsif ($bldstatus)
    {
    my $made_color;    $made_color = $good_color;
    
    print_HTML_Page( jenkinsQuery::html_OK_link( $builder, $bldnum, $rev_numb, $bld_date ),
                     $running,
                     $builder,
                     $made_color );
    }
else
    {
    $made_color = $err_color;
    if ( $is_running == 1 )
        {
        $bldnum += 1;
        $made_color = $warn_color;
        }
    print_HTML_Page( buildbotReports::is_running($is_running),
                     jenkinsQuery::html_FAIL_link( $builder, $bldnum, $is_running, $bld_date),
                     $builder,
                     $made_color );
    }
    


# print "\n---------------------------\n";
__END__

