#!/usr/bin/perl

use strict;
use warnings;
use File::Find qw(find);
use FindBin;
use lib $FindBin::Bin;
use Data::Dumper;
#use Spreadsheet::WriteExcel;
use Excel::Writer::XLSX;
use MIME::Lite;

my $opco_name = 'congo'; chomp($opco_name);
#my $opco_name = $ARGV[1]; chomp($opco_name);
my $path = $FindBin::Bin;
$path =~ s/\/bin//ig;

my $parsed_hash = {};
my $success_count_hash = {};
my $summary_dashboard = {};
my $inp_dir_hash = {};
my $day1 = `date '+%d'`; chomp($day1);
my $day2 = trim(`date '+%e'`); chomp($day2);
my $month = `date '+%b'`; chomp($month); 
my $month_date = `date '+%b %e'`; chomp($month_date);
my $curr_date = `date '+%Y-%m-%d'`; chomp($curr_date);
my $curr_date2 = `date '+%Y%m%d'`; chomp($curr_date2);
my $curr_date3 = `date '+%Y_%m_%d'`; chomp($curr_date3);
my $curr_date4 = `date '+%y%m%d'`; chomp($curr_date4);
my $curr_date5 = `date '+%A, %B %d, %Y'`; chomp($curr_date5);
my $curr_date6 = `date '+%Y/%m/%d'`; chomp($curr_date6);
my $curr_date7 = `date '+%A, %B %e, %Y'`; chomp($curr_date7);
my $pre_date1 = `date '+%Y_%m_%d' -d '-1 day'`; chomp($pre_date1);
my $pre_date2 = `date '+%Y/%m/%d' -d '-1 day'`; chomp($pre_date2);
my $pre_date3 = `date '+%Y%m%d' -d '-1 day'`; chomp($pre_date3);
my $pre_date4 = `date '+%Y-%m-%d' -d '-1 day'`; chomp($pre_date4);
my $issue1 = 'Connectivity/Password Issue';
my $excel_file = 'MTN-'.ucfirst($opco_name)."-Backup-Tracker_".$curr_date.".xlsx";
my $file_name = "$path/files/$excel_file";

my $to = ''; my $cc = '';
if (defined($ARGV[0])) {
	$to = $ARGV[0];
}
if (defined($ARGV[1])) {
        $cc = $ARGV[1];
}
#my $to = 'gnoc.1st.la.mtn.rsaa@ericsson.com,PDLFOINMTN@pdl.internal.ericsson.com,PDLHIFTMAN@pdl.internal.ericsson.com,geeta.negi@ericsson.com';
#my $cc = 'mohd.ezaz@ericsson.com,shivani.saxena@ericsson.com';

my $users_details = set_users_conf();
#print Dumper \$users_details; die;
read_opco_dir();
#print Dumper \$parsed_hash; die;
success_fail_count();
#print Dumper \$success_count_hash; die;
summary_dashboard();
create_excel();
SendMail();

sub read_opco_dir{
	my $basedir = "$path/datasrc/mtnin/backuptracker";
	opendir(DIR, "$basedir") or die "Can't open the current directory:$basedir :: $!\n";
	my @users = readdir(DIR) or die "Unable to read current dir:$!\n";
	closedir(DIR);

	foreach my $user (@users)
	{
		next if $user eq '.' || $user eq '..';
		my $user_dir = "$basedir/$user";
		read_users_dir($user_dir, $user);		
	}
}

sub read_users_dir{
	my $user_dir = shift;
	my $user = shift;

	print "$user_dir\n";
	my @hosts;
	if (-d $user_dir) {	
		opendir(DIR, "$user_dir") or die "Can't open the current directory: $user_dir::$!\n";
		@hosts = readdir(DIR) or die "Unable to read current dir:$!\n";
		closedir(DIR);
	}

	foreach my $inp_dir (@hosts){
		next if $inp_dir eq '.' || $inp_dir eq '..';
		my $inp_dir_path = "$user_dir/$inp_dir";
		if (-d $inp_dir_path)
		{	
			$inp_dir_hash->{$user}->{$inp_dir} = 1;
			read_inp($inp_dir_path, $user, $inp_dir)  
		}
	}
}

sub read_inp{
	my $inp_dir_path = shift;
	my $user = shift;
	my $inp_dir = shift;
	my ($ip, $host) = (split("_", $inp_dir))[0, 1];
	my $sdp_geo_check = 0;
	my $sdp_geo = '';
	my @cassendra_arr;
	my $cassandra_flag = 0;
	my $array_ref = $users_details->{$user};

	my $user_l = trim(lc($user));

	my @inp_files;
	if (-d $inp_dir_path) {	
		opendir(DIR, $inp_dir_path) or die "Can't open the inp_dir_path: $inp_dir_path::$!\n";
		@inp_files = readdir(DIR) or die "Unable to read inp_dir_path:$!\n";
		closedir(DIR);
	}
	my @inp_files2;
	foreach (@inp_files) { next if ($_ eq '.' || $_ eq '..'); push(@inp_files2, $_) if ($_ =~ /\.inp$/); }
	my $inp_size += map {$_} @inp_files2;
	
	if ($inp_size == 0) {
		foreach (@$array_ref) {
			$parsed_hash->{$user}->{$host}->{$ip}->{$_} = $issue1;
		}		
	}
	else 
	{
		my $nedate = readFile("$inp_dir_path/nedate.inp");
		if ($nedate =~ /$curr_date2/ig)
		{	
			foreach (@$array_ref) {
				$parsed_hash->{$user}->{$host}->{$ip}->{$_} = 'N/A';
			}
			foreach my $inp_name (@inp_files) {
				$inp_name = trim($inp_name);
				next if $inp_name eq '.' || $inp_name eq '..';
				my $inp_file = "$inp_dir_path/$inp_name";
				my $file_data = readFile($inp_file);

				##----------------- AIR Backup Check -----------------##

				if ($user_l eq 'air') {
					my $status; my $fail_reason;
					if ($inp_name =~ /backup.inp/ig) {
						($status, $fail_reason) = tape($file_data, $curr_date, $curr_date5, $inp_dir_path);
						$parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = "$status^^$fail_reason";
					}
				}

				##----------------- OCC tape Check -----------------##

				if ($user_l eq 'occ') {
					my $status; my $fail_reason;
					if ($inp_name =~ /fs_occ_backup.inp/ig) {
						($status, $fail_reason) = tape($file_data, $curr_date, $curr_date5, $inp_dir_path);
						$parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = "$status^^$fail_reason";
					}
				}	
				
				##----------------- SDP geo-redundancy and tape Check -----------------##

				if ($user_l eq 'sdp') {	
					my $status; my $fail_reason;
					if ($inp_name =~ /TTMonitorStandby.inp/ig) {
						$sdp_geo_check++;
						my @geo_str = (split("\n", $file_data));
						my $arr_len = @geo_str;
						if ($arr_len > 4) {
							$parsed_hash->{$user}->{$host}->{$ip}->{'geo-redundancy.inp'} = 'Fail';
						}
					}			
					if ($inp_name =~ /TTMonitorStandby.inp/ig && $parsed_hash->{$user}->{$host}->{$ip}->{'geo-redundancy.inp'} eq 'N/A')
					{
						#foreach my $geo_str ((split("\n", $file_data))) {
							if ($file_data =~ /$curr_date\s+\d+\:\d+\:\d+\s+Standby\s+database\s+replication\s+OK/ig) {
								$parsed_hash->{$user}->{$host}->{$ip}->{'geo-redundancy.inp'} = 'Success';
							}
							else {
								$parsed_hash->{$user}->{$host}->{$ip}->{'geo-redundancy.inp'} = 'Fail';
							}
						#}
					}
					if ($inp_name =~ /backup.inp/ig) {
						($status, $fail_reason) = tape($file_data, $curr_date, $curr_date5, $inp_dir_path);
						$parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = "$status^^$fail_reason";
					}
				}		
				
				##----------------- NGVS geo-redundancy, nfs and cassendra Check -----------------##
			if ($user_l eq 'ngvs') {
					my $status;
                                        if ($inp_name =~ /fs.inp/ig) {
                                                $status = dbn($file_data, $curr_date6, $curr_date);
                                                $parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = $status;
                                        }
                                        if ($inp_name =~ /db3.inp/ig) {
                                                $status = tape($file_data, $pre_date1, $month_date);
                                                $parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = $status;
                                        }
					if ($inp_name =~ /fs.inp/ig) {
                                                $status = zoo($file_data, $curr_date, $curr_date4);
                                                $parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = $status;
                                        }
                                }

#                                        my $status;
#                                        if ($inp_name =~ /fs.inp/ig) {
#                                                $status = dbn($file_data);
#                                                $parsed_hash->{$user}->{$host}->{$ip}->{'geo-redundancy.inp'} = $status;
#                                        }
#                                        if ($inp_name =~ /db.inp/ig) {
#                                                $status = tape($file_data, $curr_date, $curr_date5);
#                                                $parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = $status;
#                                        }
#                                        if ($inp_name =~ /d.inp/ig) {
#                                        $status = tape($file_data, $curr_date, $curr_date5);
#                                        $parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = $status;
#                                        }
#
#                                        if ($inp_name =~ /db2.inp/ig) {
#                                               $cassandra_flag++;
#                                                foreach my $date_str ((split("\n", $file_data))) {
#                                                if ($date_str =~ /^$month/ig) {
#                                                        push(@cassendra_arr, trim($date_str));
#                                                        }
#                                                }
#                                        }
#                           	         if ($inp_name =~ /fs.inp/ig) {
#                                                $status = zoo($file_data, $curr_date, $curr_date4);
#                                                $parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = $status;
#                                        }

                                        
#					}
						


				##----------------- CCN dbn Check -----------------##

				if ($user_l eq 'ccn') {
					my $status;
					if ($inp_name =~ /dbn_backup.inp/ig) {
						$status = dbn($file_data, $curr_date3, '');
						$parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = $status;
					}
				}

				##----------------- MINSAT fs and db Check -----------------##

				if ($user_l eq 'minsat') {
					my $status;
					if ($inp_name =~ /fs.inp/ig) {
						$status = filesystem($file_data, $curr_date6);
						$parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = $status;
					}
					if ($inp_name =~ /db_backup.inp/ig) {
						$status = dbn($file_data, $pre_date1, '');
						$parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = $status;
					}
				}

				##----------------- VS tape, nfs, ora, ora_archive and geo-redundancy Check -----------------##

				if ($user_l eq 'vs') {
					my $status; my $fail_reason;
					if ($inp_name =~ /oraBackup.inp/ig || $inp_name =~ /oraArchiveBackup.inp/ig) {
						$status = ora($file_data, $curr_date2);
						$parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = $status;
					}
					if ($inp_name =~ /backup.inp/ig) {
						($status, $fail_reason) = tape($file_data, $curr_date, $curr_date5, $inp_dir_path);
						$parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = $status;
					}
					if ($inp_name =~ /cassendra/ig) {
						$cassandra_flag++;
						foreach my $date_str ((split("\n", $file_data))) {
							if ($date_str =~ /^$month/ig) {
								push(@cassendra_arr, trim($date_str));
							}
						}
					}
				}

				##----------------- EMA proclog and sogconfig Check -----------------##

				if ($user_l eq 'ema') {
					my $status;
					if ($inp_name =~ /config_backup.inp/ig) {
						$status = config($file_data, $month_date, $curr_date2);
						$parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = $status;
					}
					if ($inp_name =~ /proclog.inp/ig) {
						$status = proclog($file_data, $curr_date4);
						$parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = $status;				
					}
				}

				##----------------- NGCRS appfs, archived CDR and oracle database Check -----------------##

				if ($user_l eq 'ngcrs') {
					my $status;
					if ($inp_name =~ /appfs.inp/ig) {
						$status = appfs($file_data, $pre_date3);
						$parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = $status;
					}
					if ($inp_name =~ /appfs1.inp/ig) {
						$status = cdr($file_data, $pre_date3);
						$parsed_hash->{$user}->{$host}->{$ip}->{'cdr.inp'} = $status;				
					}
					if ($inp_name =~ /maintenance.inp/ig) {
						$status = oradb($file_data, $pre_date4);
						$parsed_hash->{$user}->{$host}->{$ip}->{'oradb.inp'} = $status;
					}
				}

				##----------------- CRS appfs, archived CDR and oracle database Check,fs backup -----------------##

				if ($user_l eq 'crs') {
					my $status;
					if ($inp_name =~ /db_backup.inp/ig) {
						$status = dbn($file_data, $curr_date2, $curr_date3);
						$parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = $status;
				} 
 				if ($inp_name =~ /fs_backup.inp/ig) {
                                                $status = appfs($file_data, $curr_date2, $curr_date3);
                                                $parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} = $status;	}
				}

			}

			##------------- cassendra check -------------##
			
			my $flag = 0;
			foreach my $date_val (@cassendra_arr) {
				if ($date_val =~ /^$month\s+$day1/ig || $date_val =~ /^$month\s+$day2/ig) {
					$flag = 1;
				}
			}
			if ($cassandra_flag > 0) {	
				if ($flag == 1) {
					$parsed_hash->{$user}->{$host}->{$ip}->{'cassendra.inp'} = 'Success';
				} else {
					$parsed_hash->{$user}->{$host}->{$ip}->{'cassendra.inp'} = 'Fail';
				}
			}
			
			my $match = map { /cassendra\.inp/ig } @$array_ref;
			if ($match == 1 && $cassandra_flag == 0) {
				$parsed_hash->{$user}->{$host}->{$ip}->{'cassendra.inp'} = 'N/A';		
			}

			##------------- geo-redundancy check -------------##

			if ($sdp_geo_check == 2 && $parsed_hash->{$user}->{$host}->{$ip}->{'geo-redundancy.inp'} eq 'N/A') {
				$parsed_hash->{$user}->{$host}->{$ip}->{'geo-redundancy.inp'} = 'Success';
			}			
		}
		else {
			foreach (@$array_ref) {
				$parsed_hash->{$user}->{$host}->{$ip}->{$_} = $issue1;
			}
		}
	}
}

sub tape{
	my $data = shift;
	my $date1 = shift;
	my $date2 = shift;
	my $inp_dir_path = shift;
	my $status = ''; my $fail_reason = '';
	if ($data =~ /INFO\:root\:Filesystem\s+backup\s+ended\s+at\s+$date1/ig) {
		$status = 'Success';
	}
	elsif ($data =~ /Backup\s+completed\s+at\W+$date2/ig || $data =~ /Backup\s+completed\s+at\W+$curr_date7/ig) {
		$status = 'Success';
	}
	elsif ($data =~ /$month_date.*?voucherHistory/ig){
		$status = 'Success';
	}
#	elsif ($data =~ /cfbackup\_.*?$curr_date2.*?\.log/ig) {
#              $status = 'Success';
#	}
#	elsif ($data =~ /backup*./ig) {
#             $status = 'Success'
#	}
#	elsif ($data =~ /backuplog*/ig) {
#               $status = 'Success'
#      }
#	elsif ($data =~ /backuplog*/ig) {
#                $status = 'Success'
#	}
	else {
		$status = 'Fail';
		$fail_reason = 'BURA_BACKUP Failure' if ($status =~ /Fail/ig);
	}
	return $status;
}

sub sdp_geo{
	my $data = shift;
	my $status = '';
	my @geo_str = (split("\n", $data));
	my $arr_len = @geo_str;
	if ($arr_len > 4) {
		$status = 'Fail';
	}
	return $status;
}

sub ngvs_geo{
	my $data = shift;
	my $status = '';
	my @geo_str = split('Datacenter', $data);
	my $un_count1 = () = $geo_str[1] =~ /UN/ig;
	my $un_count2 = () = $geo_str[2] =~ /UN/ig;

	if ($geo_str[1] =~ /DC1/is && $geo_str[2] =~ /DC2/is) {
		if ($un_count1 == 15 && $un_count2 == 15) {
			$status = 'Success';
		} 
	elsif ($data =~ /cfbackup\_.*?$curr_date2.*?\.log/ig) {
        $status = 'Success';
	}	
	else {
			$status = 'Fail';
		}
	}
	return $status;
}

sub dbn{
	my $data = shift;
	my $date1 = shift;
	my $date2 = shift;
	my $status = '';
	if ($data =~ /ScheduledBackup\_$date1/ig) {
		$status = 'Success';
	}
	elsif ($data =~ /INFO\:root\:Filesystem\s+backup\s+ended\s+at\s+$date2/ig) {
                $status = 'Success';
        } 
	elsif ($data =~ /rman\_$date2.*?Recovery\s+Manager\s+complete/ig || $data =~ /Recovery\s+Manager\s+complete/ig) {
		$status = 'Success';
	}
	elsif ($data =~ /rman*/ig) {
                $status = 'Success';
	}
	elsif ($data =~ /HISTDG*/ig) {
                $status = 'Success';
	} 
	elsif ($data =~ /cfbackup\_.*?$curr_date2.*?\.log/ig) {
	$status = 'Success';
	}
	elsif ($data =~ /DUMP\s+is\s+complete/ig) {
		$status = 'Success';
	} else {
		$status = 'Fail';
	}
	return $status;
}

sub filesystem{
	my $data = shift;
	my $date = shift;
	my $status = '';
	if ($data =~ /$curr_date6.*?Backup\s+completed/ig) {
		$status = 'Success';
	} else {
		$status = 'Fail';
	}
	return $status;
}

sub ora{
	my $data = shift;
	my $date = shift;
	my $status = '';
	if ($data =~ /This\s+backup\W+$date.*?session\s+is\s+completed\s+and\s+finished/ig) {
		$status = 'Success';
	} else {
		$status = 'Fail';
	}
	return $status;
}

sub proclog{
	my $data = shift;
	my $mdate = shift;
	my $date = shift;
	my $status = '';
	if ($data =~ /.*?$curr_date2/ig) {
		$status = 'Success';
	} else {
		$status = 'Fail';
	}
	return $status;
}

sub config{
	my $data = shift;
	my $date = shift;
	my $status = '';
	if ($data =~ /sogconfig\_.*?$curr_date4/ig) {
		$status = 'Success';
	}
	 else {
		$status = 'Fail';
	}
	return $status;
}

sub appfs{
	my $data = shift;
	my $date = shift;
	my $status = '';
	if ($data =~ /root_backup\_.*?$date/ig) {
		$status = 'Success';
	} else {
		$status = 'Fail';
	}
	return $status;
}

sub cdr{
	my $data = shift;
	my $date = shift;
	my $status = '';
	if ($data =~ /swezdesma\_$date/ig) {
		$status = 'Success';
	} else {
		$status = 'Fail';
	}
	return $status;
}

sub oradb{
	my $data = shift;
	my $date = shift;
	my $status = '';
	if ($data =~ /rman\_bkup\_$date/ig) {
		$status = 'Success';
	} else {
		$status = 'Fail';
	}
	return $status;
}

sub zoo{
	my $data = shift;
	my $date = shift;
	my $status = '';
	if ($data =~ /INFO\:root\:Filesystem\s+backup\s+ended\s+at\s+$date/ig) {
                $status = 'Success';
        }
        elsif ($data =~ /Backup\s+completed\s+at\W+$date/ig) {
                $status = 'Success';
	} else { 
		$status = 'Fail';
	}
#	if ($data =~ /cfbackup\_.*?$curr_date4.*?\.log/ig) {
#		$status = 'Success';
#       }
#	if ($data =~ /daily\_db*/ig) {
#                $status = 'Success';
#	}
#	if ($data =~ /Jun*/ig) {
#                $status = 'Success';	}
	return $status;
}

##==========================================================================##

sub create_excel{
	my $workbook  = Excel::Writer::XLSX->new($file_name);
	#$workbook->set_optimization();	

	my $heading = $workbook->add_format(align => 'center', bold	=> 1, text_wrap	=> 1, top => 1, left => 1, right => 1, bottom => 1);
	$heading->set_text_wrap();

	my $cell_format = $workbook->add_format(center_across => 1, bold => 1, pattern => 1, border => 6, fg_color => 'green', align => 'vcenter', top => 1, left	=> 1, right	=> 1, bottom => 1, text_wrap => 1);

	my $format1 = $workbook->add_format(color => 'white', bold => 1, bg_color=>'#0066ff', border=>1);
	my $format2 = $workbook->add_format(color => 'black', bold => 1, bg_color=>'#ff0099', border=>1);
	my $format3 = $workbook->add_format(color => 'yellow', bold => 1, bg_color=>'green', border=>1);
	my $format4 = $workbook->add_format(color => 'black', bg_color=>'yellow', valign => 'vcenter', align => 'center', border=>1);
	my $format5 = $workbook->add_format(color => 'black', bg_color=>'#ccff00', valign => 'vcenter', align => 'center', border=>1);
	my $format6 = $workbook->add_format(valign => 'vcenter', align => 'center', border=>1);
	my $format7 = $workbook->add_format(bg_color => '#ff9999', valign => 'vcenter', align => 'center', border=>1);
	my $format8 = $workbook->add_format(color => 'white', bg_color => '#336699', valign => 'vcenter', align => 'center', bold => 1,);
	my $format9 = $workbook->add_format(valign => 'vcenter', align => 'center', bold => 1, border=>1);


	my $dashboard_sheet = $workbook->add_worksheet('Summary');
	my $merge1 = $workbook->add_format(color => 'white', border => 1, valign => 'top', align => 'center', bold => 1, bg_color => '#336699');
	my $merge2 = $workbook->add_format(border => 1, valign => 'top', align => 'center', bold => 1);
	create_summary($dashboard_sheet, $merge1, $merge2, $format6, $format8, $format9);
		
	my $done = 0; my $not_done = 0; my $success_count_hash2 = {};
	foreach my $user (keys %$parsed_hash) {
		if ($done > 0 || $not_done > 0) {
			$done = 0; $not_done = 0;
		}		

		my $row_num = 6;
		my $worksheet = $workbook->add_worksheet(uc($user));
		set_sheet_headers($user, $worksheet, $row_num, $format1, $format2, $format3, $format4, $format6);
		
		my $border_text = '';
		my $host_hash = $parsed_hash->{$user};	
		foreach my $host (keys %$host_hash) {
			
			my $ip_hash = $parsed_hash->{$user}->{$host};
			foreach my $ip (keys %$ip_hash) {
						
				$row_num++;
				my $i = 1;
				my $inp_hash = $parsed_hash->{$user}->{$host}->{$ip};
				my $fail_col = keys %$inp_hash;
				foreach my $inp_name (keys %$inp_hash) {	
					my ($status, $fail_reason) = (split('\^\^',$parsed_hash->{$user}->{$host}->{$ip}->{$inp_name}))[0,1];
					$status = 'Done' if ($status =~ /Success/ig);
					$status = 'Not Done' if ($status =~ /Fail/ig);
					$status = 'Connection Failure' if ($status =~ /connection_fail/ig);
					$fail_reason = 'N/A' if ($fail_reason eq '');

					$worksheet->write($row_num, 0, uc($host), $format6);
					$worksheet->write($row_num, 1, $ip, $format6);					

					my $temp_ref = $users_details->{$user};
					my $j = 0; my $fail_flag = 1;
					foreach my $col_name (@$temp_ref) {
						$j++;
						$col_name = trim($col_name);
						$inp_name = trim($inp_name);			
						if ($inp_name eq $col_name) {
							my $col_num = $i + $j;
							$border_text .= "$row_num##$col_num\n";
							$worksheet->write($row_num, $col_num, $status, $format6);
							if ($status eq $issue1) {
								$worksheet->write($row_num, $col_num, $status, $format7);
							}
						}
						else {
							#my $col_num = $i + $j;
							#if ($border_text !~ /$row_num\#\#$col_num/ig) {
								#$worksheet->write($row_num, $col_num, '', $format6);
							#}
						}
					}				
                                        $worksheet->write($row_num, $fail_col+2, $fail_reason, $format6);
				}
			}
		}
		set_final_countings($user, $worksheet, $format5, $format6);				
	}
	$workbook->close();
}

sub create_summary{
	my $dashboard_sheet = shift;
	my $merge1 = shift;
	my $merge2 = shift;
	my $format6 = shift;
	my $format8 = shift;
	my $format9 = shift;
	$format6->set_text_wrap();

	$dashboard_sheet->set_column( 'A1:A1', 20 );
	$dashboard_sheet->set_column( 'B1:B1', 25 );
	$dashboard_sheet->set_column( 'C1:C1', 30 );
	$dashboard_sheet->set_column( 'D1:E1', 20 );

	$dashboard_sheet->write(0, 0, "Node Type", $format8);
	$dashboard_sheet->write(0, 1, "Type of Backups", $format8);
	$dashboard_sheet->write(0, 2, "Total Number of Backups", $format8);
	$dashboard_sheet->write(0, 3, "Backup Successful", $format8);
	$dashboard_sheet->write(0, 4, "Backup Failed", $format8);

	my $row = 1;
	my $col = 0;
	my $summary = $summary_dashboard->{summary};
	foreach my $node_type (keys %$summary) {		
		
		my $bkp_fail = $summary->{$node_type}->{'bkp_fail'};
		my $bkp_succ = $summary->{$node_type}->{'bkp_succ'};
		my $total = $summary->{$node_type}->{'total'};
		my $bkp_type = $summary->{$node_type}->{'bkp_type'};
		
		$dashboard_sheet->write($row, 0, uc($node_type), $format6);
		$dashboard_sheet->write($row, 1, $bkp_type, $format6);
		$dashboard_sheet->write($row, 2, $total, $format6);
		$dashboard_sheet->write($row, 3, $bkp_succ, $format6);
		$dashboard_sheet->write($row, 4, $bkp_fail, $format6);
		
		$row++;
	}
	$dashboard_sheet->write($row, 1, 'Total', $format9);
	$dashboard_sheet->write($row, 2, $summary_dashboard->{dashboard}->{total}, $format9);
	$dashboard_sheet->write($row, 3, $summary_dashboard->{dashboard}->{total_succ}, $format9);
	$dashboard_sheet->write($row, 4, $summary_dashboard->{dashboard}->{total_fail}, $format9);
	$row++;$row++;	
	$dashboard_sheet->merge_range($row, 1, $row, 2, 'Performance', $merge1);
	$dashboard_sheet->merge_range($row, 3, $row, 4, $summary_dashboard->{dashboard}->{performance}, $merge2);
}

sub set_sheet_headers{
	my $user = shift;
	my $worksheet = shift;
	my $row_num = shift;
	my $format1 = shift;
	my $format2 = shift;
	my $format3 = shift;
	my $format4 = shift;
	my $format6 = shift;

	$worksheet->set_column( 'A1:A1', 30 );
	$worksheet->set_column( 'B1:B1', 20 );
	$worksheet->set_column( 'C1:Z1', 25 );

	$worksheet->write(1, 0, "Total ". uc($user) ." nodes Backup", $format1);
	$worksheet->write(2, 0, "Backup Failed", $format2);
	$worksheet->write(3, 0, "Backups successful", $format3);
		
	my $col_num = 0;
	$worksheet->write($row_num, $col_num, 'Node-Name', $format4);
	$col_num++;
	$worksheet->write($row_num, $col_num, 'Node-IP', $format4);
	my $header_ref = $users_details->{$user};
	foreach my $inp_name (@$header_ref) {
		my $col_name = uc($inp_name);
		$col_name =~ s/\.inp//ig;
		$col_name = trim($col_name);
		$col_num++;
		$worksheet->write($row_num, $col_num, $col_name, $format4);
	}
	$col_num++;
	$worksheet->write($row_num, $col_num, 'Fail Reason', $format4);
	my $user_hash = $inp_dir_hash->{$user};
	foreach (keys %$user_hash) {
		$row_num++;
		$worksheet->write($row_num, $col_num, '', $format6);
	}
}

sub set_final_countings{
	my $user = shift;
	my $worksheet = shift;
	my $format5 = shift;
	my $format6 = shift;

	my $col_num = 0; my $row_num = 0;
	my $inp_hash = $success_count_hash->{$user};
	foreach my $inp_name (keys %$inp_hash) {
		$col_num++;
		my $col_name = uc($inp_name);
		$col_name =~ s/\.inp//ig;
		$worksheet->write($row_num, $col_num, $col_name, $format5);

		my $total = $success_count_hash->{$user}->{$inp_name}->{total};
		my $success = $success_count_hash->{$user}->{$inp_name}->{success};
		my $fail = $success_count_hash->{$user}->{$inp_name}->{fail};
		$worksheet->write(1, $col_num, $total, $format6);
		$worksheet->write(2, $col_num, $fail, $format6);
		$worksheet->write(3, $col_num, $success, $format6);		
	}
}

sub success_fail_count{	
	foreach my $user (keys %$parsed_hash) {
		my $host_hash = $parsed_hash->{$user};
		foreach my $host (keys %$host_hash) {	
			my $ip_hash = $parsed_hash->{$user}->{$host};
			foreach my $ip (keys %$ip_hash) {
				my $inp_hash = $parsed_hash->{$user}->{$host}->{$ip};
				foreach my $inp_name (keys %$inp_hash) {
					if ($parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} =~ /Success/ig) {
						$success_count_hash->{$user}->{$inp_name}->{success} += 1;
					} else {
						$success_count_hash->{$user}->{$inp_name}->{success} += 0;
					}
					if ($parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} =~ /Fail/ig) {
						$success_count_hash->{$user}->{$inp_name}->{fail} += 1;
					}
					else {
						$success_count_hash->{$user}->{$inp_name}->{fail} += 0;
					}

					$success_count_hash->{$user}->{$inp_name}->{total} += 1;
					if ($parsed_hash->{$user}->{$host}->{$ip}->{$inp_name} eq 'N/A') {
						$success_count_hash->{$user}->{$inp_name}->{total} -= 1;
					}
				}
			}
		}
	}
}

sub summary_dashboard{
	my $total = 0; my $total_succ = 0; my $total_fail = 0;
	my $summary_hash = {};
	foreach my $user (keys %$success_count_hash)
	{
		my $succ_count = 0; my $fail_count = 0; my $total_per_user = 0;
		my $bkps = '';
		my $user_hash = $success_count_hash->{$user};
		foreach my $inp_name (keys %$user_hash) {			
			$succ_count = $succ_count+$user_hash->{$inp_name}->{success};
			$fail_count = $fail_count+$user_hash->{$inp_name}->{fail};
			$total_per_user = $total_per_user+$user_hash->{$inp_name}->{total};

			my $bkp_name = uc($inp_name);
			$bkp_name =~ s/\.inp//ig;
			$bkps .= "$bkp_name Backup / ";
		}
		$total = $total+$total_per_user;
		$total_succ = $total_succ+$succ_count;
		$total_fail = $total_fail+$fail_count;
		$bkps =~ s/\s*\/\s*$//ig;

		$summary_hash->{$user}->{'bkp_type'} = $bkps;
		$summary_hash->{$user}->{'total'} = $total_per_user;
		$summary_hash->{$user}->{'bkp_succ'} = $succ_count;
		$summary_hash->{$user}->{'bkp_fail'} = $fail_count;
	}
	my $performance = ($total_succ/$total)*100 if ($total != 0);
	$summary_dashboard->{summary} = $summary_hash;
	$summary_dashboard->{dashboard}->{total} = $total;
	$summary_dashboard->{dashboard}->{total_succ} = $total_succ;
	$summary_dashboard->{dashboard}->{total_fail} = $total_fail;
	$summary_dashboard->{dashboard}->{performance} = $performance;
}

sub set_users_conf{
	my $users_details = {};
	my $conf_file = "$path/conf/pma_bkp_tracker.conf";
	open FH, "< $conf_file" or die "Can't open the users details file $conf_file: $!\n";
	while (<FH>) {
		chomp $_;
		my ($user, $inp_names) = (split("=", $_))[0, 1];
		if (defined($inp_names)) {
			my $user_upper = uc($user);
			my @temp_array = my @temp_array2 = sort {$a cmp $b} (split(",", $inp_names));
			$users_details->{$user} = \@temp_array;
			$users_details->{$user_upper} = \@temp_array2;
		}
	}
	return $users_details;
}

sub SendMail{
	#my $to = 'mohd.ezaz@ericsson.com,kratika.gandhi@ericsson.com,sunil.sharma@ericsson.com,trilokesh.visoriya@ericsson.com,patel.apurv.vishnuprasad@ericsson.com';
	#my $cc = '';
	my $from = 'MTN.Backup.Tracker@ericsson.com';
	my $subject = "MAIL TEST";
	my $messageBody = "Please find the attachment";

	my $msg = MIME::Lite->new(
			From     => $from,
			To       => $to,
			Cc       => $cc,
			Subject  => 'MTN '.ucfirst($opco_name)."-Backup-Tracker",			
			#Type     => 'application/excel',
			Encoding => '8bit',
			Data     => "Hi Team,

Please find the attached ".ucfirst($opco_name)."-Backup-Tracker of $curr_date.
	
Thanks"
        );
	my ($mime_type, $encoding) = ('application/xls', 'base64');

	$msg->attach(
			Type     => $mime_type, #'image/gif',
			Encoding => $encoding ,
			Path     => "$path/files/$excel_file",
			Filename => $excel_file,
			Disposition => 'attachment'
		);

	# Sending the mail to Mail Server.
	if ($msg->send('smtp')) {
		print "Email Sent Successfully\n";
	}else {
		print "Problem in sending mail\n";
	}
}

sub readFile{
	my $file = shift;
	my $data = '';
	open (FH2,"< $file") or die "Can't open the current file $file: $!\n";
	while(<FH2>){
		chomp $_;
		$data .= $_."\n";
	}
	chomp($data);
	return $data;
}

sub trim{
	my $data = shift;
	$data =~ s/^\s+//;
	$data =~ s/\s+$//;
	return $data;
}
