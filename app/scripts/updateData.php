<?php

# 初始化 EloquentORM
require "/opt/webs/music-163/app/scripts/database.php";

# 建立模型
class Jobs extends Model
{
}

# 拿到所有的企业数据
$jobs = Jobs::get();
foreach ($jobs as $index => $item) {

	# 拿到数据
	$job = Jobs::find($item->id);

	# 处理LOGO ,删除缩略图相关的字符
	$job->logo = str_replace('/thumbnail_120x120', '', $item->logo);

	# 要求处理成JSON 第一次处理
	$job->li_b_l = str_replace("\\n", '', json_encode(explode(' / ', substr($job->li_b_l, strripos($job->li_b_l, 'k') + 1)), JSON_UNESCAPED_UNICODE));

	# 把要求处理成JSON 第二次处理 ,实例上1 2 可以合并
	$job->li_b_l = json_encode([
		explode('-', preg_replace('/年|经验|\\n/', '', json_decode($job->li_b_l, true)[0])),
		json_decode($job->li_b_l, true)[1]
	], JSON_UNESCAPED_UNICODE);

	# 处理的地址为JSON
	$job->address = json_encode(explode('·', $job->address), JSON_UNESCAPED_UNICODE);

	# 加入公司的级别 ,结果类似 A轮 B轮
	$job->level = json_decode($job->industry, true)[1];

	# 处理公司行业为JSON
	$job->industry = json_encode(explode(',', json_decode($job->industry, true)[0]), JSON_UNESCAPED_UNICODE);

	# 处理企业所在位置的经纬度
	$latng = getLatLng(implode(json_decode($item->address, true), ''));
	$job->lat = (string)$latng[0];
	$job->lng = (string)$latng[1];

	# 保存
	$job->save();

	# 控制台打印 ID
	var_dump($job->id);
}

/**
 * 下载LOGO
 * @param $logo 图片名字
 * @param string $path 储存的地址
 * @return bool 成功 : 全路径 | 失败 False
 */
function downLogoImg($logo, $path = './logos/')
{
	$ext = substr($logo, strripos($logo, '.'));
	$fileName = hash('sha128', uniqid());
	$file = $path . $fileName . $ext;
	if (file_put_contents($file, file_get_contents($logo))) {
		return $fileName;
	}

	return false;
}

/**
 * 利用百度地图 解析地址为经纬度
 * @param $address 地址
 * @return array 经纬度结果集
 */
function getLatLng($address)
{
	$url = 'http://api.map.baidu.com/geocoder/v2/?address=' . $address . '&output=json&ak=你的AK';
	$lngAndLat = file_get_contents($url);
	$result = json_decode($lngAndLat)->result;
	return [
		$result->location->lat,
		$result->location->lng,
	];
}
