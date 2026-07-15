"""Small labeled retrieval set. Add real manuals and cases before resume use."""

RAG_EVAL_DATASET = [
    {"query": "EarPro连不上手机怎么重新配对", "expected_id": "earpro-connect-01"},
    {"query": "EarPro左边没有声音", "expected_id": "earpro-audio-01"},
    {"query": "EarPro掉水里还能放回盒子充电吗", "expected_id": "earpro-water-01"},
    {"query": "EarLite怎么重新连接蓝牙", "expected_id": "earlite-connect-01"},
    {"query": "EarLite充电灯不亮", "expected_id": "earlite-charge-01"},
    {"query": "WatchPro充电特别慢", "expected_id": "watchpro-charge-01"},
    {"query": "WatchPro屏幕点不动", "expected_id": "watchpro-screen-01"},
    {"query": "WatchPro后盖鼓起来而且发热", "expected_id": "watchpro-battery-01"},
    {"query": "WatchS更新到一半要注意什么", "expected_id": "watchs-update-01"},
    {"query": "WatchS能戴着洗热水澡吗", "expected_id": "watchs-water-01"},
    {"query": "Band5在应用里一直离线", "expected_id": "band5-offline-01"},
    {"query": "Band6测心率不准确", "expected_id": "band6-heart-01"},
    {"query": "EarPro降噪感觉没效果", "expected_id": "earpro-noise-01"},
    {"query": "EarPro打电话对方听不清", "expected_id": "earpro-mic-01"},
    {"query": "EarPro升级固件要多少电", "expected_id": "earpro-update-01"},
    {"query": "EarLite听歌声音一顿一顿", "expected_id": "earlite-audio-01"},
    {"query": "EarLite为什么只有一个耳机工作", "expected_id": "earlite-mono-01"},
    {"query": "EarLite充电盒能淋雨吗", "expected_id": "earlite-water-01"},
    {"query": "EarLite充电盒鼓起来了", "expected_id": "earlite-battery-01"},
    {"query": "WatchPro跑步一直定不了位", "expected_id": "watchpro-gps-01"},
    {"query": "WatchPro测出来的心率不准", "expected_id": "watchpro-heart-01"},
    {"query": "WatchPro可以戴着蒸桑拿吗", "expected_id": "watchpro-water-01"},
    {"query": "WatchS磁吸充电没反应", "expected_id": "watchs-charge-01"},
    {"query": "WatchS微信消息不提醒", "expected_id": "watchs-notify-01"},
    {"query": "WatchS换手机会不会丢运动数据", "expected_id": "watchs-pair-01"},
    {"query": "WatchS后盖翘起还有异味", "expected_id": "watchs-battery-01"},
    {"query": "Band5夹上充电器还是不开机", "expected_id": "band5-charge-01"},
    {"query": "Band5昨晚睡觉没有记录", "expected_id": "band5-sleep-01"},
    {"query": "Band5收不到手机通知", "expected_id": "band5-notify-01"},
    {"query": "Band5可以潜水使用吗", "expected_id": "band5-water-01"},
    {"query": "Band5恢复出厂前需要同步吗", "expected_id": "band5-reset-01"},
    {"query": "Band6充一晚上还没满", "expected_id": "band6-charge-01"},
    {"query": "Band6有震动但是黑屏", "expected_id": "band6-screen-01"},
    {"query": "Band6跑步记录自己停了", "expected_id": "band6-workout-01"},
    {"query": "Band6游泳后要怎么处理", "expected_id": "band6-water-01"},
    {"query": "Band6突然很烫还有味道", "expected_id": "band6-battery-01"}
]

NO_ANSWER_CASES = [
    "EarPro能不能连接卫星电话",
    "WatchS能测血糖并用于诊断吗",
    "Band6在哪里更换SIM卡",
    "EarLite支持水下录音吗"
]
