<?php

/**
 * Design by xiangli.
 * License: Closed source.
 * Date: 17-12-4 - 上午9:08.
 * Powered By: IntelliJ IDEA.
 * Description:
 *
 * 数据库链接
 */

use Illuminate\Database\Capsule\Manager as Capsule;

require_once '/opt/webs/music-163/vendor/autoload.php';

# 初始化EloquentORM

$capsule = new Capsule;

$capsule->addConnection([
	'driver' => 'mysql',
	'host' => '127.0.0.1',
	'database' => 'music',
	'username' => 'music',
	'password' => 'root',
	'charset' => 'utf8',
	'collation' => 'utf8_general_ci',
	'prefix' => ''
]);
$capsule->bootEloquent();