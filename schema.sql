-- 创建表，如果表已存在则跳过
CREATE TABLE IF NOT EXISTS image_host (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    key_or_cookie TEXT,
    is_available BOOLEAN NOT NULL,
    is_proxy BOOLEAN NULL
);

-- 插入数据
INSERT OR IGNORE INTO image_host (id,name, url, key_or_cookie, is_available,is_proxy)
VALUES (1,'Pter', 'https://s3.pterclub.com', 'cookie', 1,0);

INSERT OR IGNORE INTO image_host (id,name, url, key_or_cookie, is_available,is_proxy)
VALUES (2,'兰空图床', 'http://175.178.123.76:40027', '', 1,0);

INSERT OR IGNORE INTO image_host (id,name, url, key_or_cookie, is_available,is_proxy)
VALUES (3,'pixhost', 'https://api.pixhost.to/images', '', 1,0);

CREATE TABLE IF NOT EXISTS downloader(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type int NOT NULL,
    url TEXT NOT NULL,
    user TEXT not null,
    password TEXT not null,
    seeding_path TEXT
);


CREATE TABLE IF NOT EXISTS site (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type int NOT NULL UNIQUE,
    cookie TEXT not null,
    is_available BOOLEAN DEFAULT 1
);


CREATE TABLE IF NOT EXISTS screenshot(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dir TEXT NOT NULL,
    num INTEGER NOT NULL,
    complexity REAL NOT NULL,
    is_thumbnail BOOLEAN DEFAULT 1,
    thumbnail_horizontal INTEGER NOT NULL,
    thumbnail_vertical INTEGER NOT NULL,
    starting_point REAL NOT NULL,
    end_point REAL NOT NULL,
    auto_upload  BOOLEAN DEFAULT 1,
    del_local_img BOOLEAN DEFAULT 0
);

INSERT INTO screenshot (id,dir,num,complexity,is_thumbnail,thumbnail_horizontal,thumbnail_vertical,
                                            starting_point,end_point,auto_upload,del_local_img)
VALUES (1,'temp/pic',3,0.02,true,4,4,
        0.12,0.92,true,false);

CREATE TABLE IF NOT EXISTS pt_gen(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    is_available BOOLEAN DEFAULT 1
);

INSERT OR IGNORE INTO pt_gen(id,name, url, is_available)
VALUES (1,'末日PTGEN','https://ptgen.agsvpt.work/',true);


CREATE TABLE IF NOT EXISTS configuration(
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_host_id INTEGER NOT NULL,
    pt_gen_id INTEGER NOT NULL,
    screenshot_id INTEGER NOT NULL,
    downloader_id INTEGER NOT NULL,
    is_transfer BOOLEAN DEFAULT 0,
    transfer_dir TEXT,
    proxy_url TEXT,
    torrent_path TEXT
);

INSERT OR IGNORE INTO configuration(id ,image_host_id, pt_gen_id, screenshot_id, downloader_id, is_transfer, transfer_dir, proxy_url, torrent_path)
VALUES (1,1,1,1,0,false,'','','')