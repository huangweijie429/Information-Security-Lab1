<?php
/*
 * phpMyAdmin configuration for the CVE-2018-12613 lab.
 * "config" auth mode logs in automatically as the test user, exactly as in the
 * public Vulhub environment, so the vulnerable endpoint needs no manual login.
 */
$i = 0;

$i++;
$cfg['Servers'][$i]['verbose'] = 'mysql';
$cfg['Servers'][$i]['host'] = 'mysql';
$cfg['Servers'][$i]['port'] = 3306;
$cfg['Servers'][$i]['socket'] = '';
$cfg['Servers'][$i]['connect_type'] = 'tcp';
$cfg['Servers'][$i]['auth_type'] = 'config';
$cfg['Servers'][$i]['user'] = 'test';
$cfg['Servers'][$i]['password'] = 'test';

$cfg['blowfish_secret'] = '5af02eda401ae8.69737537';
$cfg['DefaultLang'] = 'en';
$cfg['ServerDefault'] = 1;
$cfg['UploadDir'] = '';
$cfg['SaveDir'] = '';
