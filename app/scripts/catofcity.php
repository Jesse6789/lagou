<?php

/**
 * Design by xiangli.
 * License: Closed source.
 * Date: 17-12-4 - 上午9:08.
 * Powered By: IntelliJ IDEA.
 * Description:
 *
 * 按城市分类
 */

use Illuminate\Database\Eloquent\Model;

require "/opt/webs/music-163/app/scripts/database.php";

class Job extends Model
{
}

$jobs = Job::get();

$data = [];
foreach ($jobs as $job) {
	if ($job->id < 3137) continue;
	$item = Job::find($job->id);;
	$latng = getLatLng(implode(json_decode($item->address, true), ''));
	$item->lat = (string)$latng[0];
	$item->lng = (string)$latng[1];
	$item->save();

	var_dump($item->id);


//	$city = json_decode($job->address, true);
//	$data[$city[0]][$job->type][$job->level][$job->name] = json_decode(json_encode($job));
}


//
//echo json_encode($data);
