
# 山手線アプリ

## 概要

山手線アプリは、Snowflakeの地理空間型を使用し、駅の位置を地図上で表示することができるアプリです。
また、駅の緯度経度や駅間の距離を検索することもできます。

## 前提条件

・Snowflakeが使用できること

	無料トライアル申し込みサイト（30日間の無料トライアル）：
	https://signup.snowflake.com/
	
・Snowflakeに山手線情報が入ったテーブルが作成されていること

	（テーブル作成手順）
	1. 下記クエリで任意のデータベースにテーブルを作成する
		** クエリ ***************************************************
		CREATE OR REPLACE TABLE "<データベース名>"."＜スキーマ名＞"."YAMANOTELINE_MAINDATA"
		(STATION_NAME VARCHAR(16777216), 
		LONGITUDE FLOAT,
		LATITUDE FLOAT,
		LONGITUDE_LATITUDE GEOGRAPHY,
		PASSENGERS NUMBER(38,0)
		);
		***************************************************************

	2. Snowflake Web UI右上の[データベース]をクリックし手順1で作成したテーブルを開き、[データをロード]をクリックする
	
	3. [ソースファイル]選択画面より、配布したYamanoteLineData.csvを選択し、データをロードする

	参考サイト：
	https://knowledge.insight-lab.co.jp/snowflake/beginner/local-load

## 設定手順
・config_yamanote.iniファイルを開き、[SNOWFLAKE]に作成したSnowflakeテーブルの情報を記載する
	例：[SNOWFLAKE]
		MAIN_TABLE = "GEO_DB"."PUBLIC"."YAMANOTELINE_MAINDATA"

・Streamlit Cloud アプリデプロイ設定手順

	1. Streamlit Cloud アプリ作成画面の「New app」をクリックする

	2. 「Paste GitHub URL」をクリックする

	3. 下記のURLを貼る
	URL：
	https://github.com/masudarina/Streamlit_YamanoteLineApp/blob/main/YamanoteLineApp.py

	4. 「Advanced settings...」をクリックし、「Secrets」に下記を入力し内容を保存する
	--------------------------------------------------------------------------
	SF_USER = <Snowflakeのユーザ名を記載してください>
	SF_PASSWORD = <Snowflakeユーザのパスワード記載してください>
	SF_ACCOUNT = <Snowflakeのアカウント識別子を記載してください>
	# 例：SF_ACCOUNT = "cd12321.ap-northeast-1.aws"
	# SF_ROLE =  <使用するロールを記載してください>
	# SF_WAREHOUSE =  <デフォルトのウェアハウスが設定されていない場合は使用するウェアハウスを記載してください>
	--------------------------------------------------------------------------

・Streamlit Cloud アプリ共有設定手順

	1. Streamlit Cloud アプリ作成画面を開き、共有したいアプリの３点リーダーをクリックする

	2. 「Settings」＞「Sharing」をクリックする

	2. 「Invite viewers by email」に閲覧者のメールアドレスを記入し、「Save」をクリックする
	参考サイト：
	https://docs.streamlit.io/streamlit-cloud/get-started/share-your-app

## 使用手順

Streamitからの招待メールを開き、「Accept invite and visit app」を押下する
	参考サイト：
	https://docs.streamlit.io/streamlit-cloud/get-started/share-your-app

新規作成　2022/11/16
