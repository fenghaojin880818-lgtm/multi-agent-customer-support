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
    {"query": "Band6测心率不准确", "expected_id": "band6-heart-01"}
]
