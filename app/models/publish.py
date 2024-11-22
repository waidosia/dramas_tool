# CREATE TABLE IF NOT EXISTS publish_history(
#     Id INTEGER PRIMARY KEY AUTOINCREMENT,
#     cn_name TEXT NOT NULL,
#     en_name TEXT NOT NULL,
#     year INTEGER NOT NULL,
#     season INTEGER NOT NULL,
#     film_source TEXT NOT NULL,
#     source TEXT NOT NULL,
#     team TEXT NOT NULL,
#     cover TEXT NOT NULL,
#     pt_gen TEXT,
#     introduction TEXT NOT NULL,
#     category TEXT NOT NULL,
#     main_title TEXT NULL,
#     sub_title TEXT NULL ,
#     torrent_path TEXT NULL,
#     torrent BLOB,
#     screenshot1_link TEXT NULL,
#     screenshot2_link TEXT NULL,
#     screenshot3_link TEXT NULL,
#     screenshot4_link TEXT NULL,
#     screenshot5_link TEXT NULL,
#     video_screenshot_link  TEXT NULL,
#     publish_info  TEXT NULL,
#     mediaInfo  TEXT NULL,
#     reference TEXT NULL,
#     group_icon TEXT NULL,
#     videoInfo_icon TEXT NULL,
#     screenshot_icon TEXT NULL,
#     first_file_name TEXT NULL
# );

from app.extension import db

class Publish(db.Model):
    __tablename__ = 'publish_history'
    # 列
    id = db.Column(db.Integer, primary_key=True)
    cn_name = db.Column(db.String(100), nullable=False)
    en_name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    season =db.Column(db.Integer, nullable=False)
    film_source = db.Column(db.String(100), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    team =db.Column(db.String(100), nullable=False)
    cover = db.Column(db.String(100), nullable=False)
    pt_gen = db.Column(db.String(100), nullable=False)
    introduction = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    main_title = db.Column(db.String(100), nullable=False)
    sub_title = db.Column(db.String(100), nullable=False)
    torrent_path = db.Column(db.String(100), nullable=False)
    torrent = db.Column(db.LargeBinary, nullable=False)
    screenshot1_link =db.Column(db.String(100), nullable=False)
    screenshot2_link =db.Column(db.String(100), nullable=False)
    screenshot3_link =db.Column(db.String(100), nullable=False)
    screenshot4_link =db.Column(db.String(100), nullable=False)
    screenshot5_link =db.Column(db.String(100), nullable=False)
    video_screenshot_link =db.Column(db.String(100), nullable=False)
    publish_info =db.Column(db.String(100), nullable=False)
    mediaInfo =db.Column(db.String(100), nullable=False)
    reference = db.Column(db.String(100), nullable=False)
    group_icon = db.Column(db.String(100), nullable=False)
    videoInfo_icon = db.Column(db.String(100), nullable=False)
    screenshot_icon = db.Column(db.String(100), nullable=False)
    first_file_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return self.name

    def to_dict(self):
        return {
        'id': self.id,
        'cnName': self.cn_name,
        'enName': self.en_name,
        'year': self.year,
        'season': self.season,
        'filmSource':  self.film_source,
        'source':  self.source,
        'team':  self.team,
        'cover': self.cover,
        'ptGen':  self.pt_gen,
        'introduction':  self.introduction,
        'category':  self.category,
        'mainTitle': self.main_title,
        'subTitle': self.sub_title,
        'torrentPath': self.torrent_path,
        # 'screenshotLink': self.screenshot1_link,
        # 'screenshotPath': self.screenshot2_link,
        'videoScreenshotLink': self.video_screenshot_link,
        'publishInfo': self.publish_info,
        'mediaInfo':  self.mediaInfo,
        'reference': self.reference,
        'groupIcon': self.group_icon,
        'videoInfoIcon': self.videoInfo_icon,
        'screenshotIcon': self.screenshot_icon,
        'firstFileName': self.first_file_name,
        }

