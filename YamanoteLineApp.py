##**************************************************************************
## システム名   :山手線アプリ
## 業務名   :NTTD_Snowflake支援業務
##-------------------------------------------------------------------------
## 更新履歴
##  2022.11.14  益田理菜  初版
##  XXXX.XX.XX  XX XX  インシデントNO:00000  XXX対応
##*************************************************************************

##################################################
# モジュールインポート 
##################################################
import streamlit as st                      
from streamlit_folium import st_folium      
import folium                               
import pandas as pd                         
import snowflake.connector
from PIL import Image
import configparser
import os

##################################################
# パラメーター設定 
##################################################
current_path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(current_path, 'config_yamote.ini')
# config_ini = configparser.ConfigParser()
# config_ini.read(path, encoding='utf-8')
yamanote_image = os.path.join(current_path, 'yamote.jpg')

##################################################
# 変数設定
##################################################
# 画像のパス
image = Image.open(yamanote_image)

# Snowflake情報
sf_user = st.secrets["sf_user"]
sf_password = st.secrets["sf_password"]
sf_account = st.secrets["sf_account"]
main_table = st.secrets["main_table"]
# (保存用)ユーザーによっては以下必須
# sf_role = st.secrets["sf_role"]
# sf_warehouse = st.secrets["sf_role"]

# 運行情報リンク
link = '[🚞山手線（関東エリア）運行情報・運休情報](https://traininfo.jreast.co.jp/train_info/line.aspx?gid=1&lineid=yamanoteline)'

##################################################
# エラーハンドリング設定
##################################################
try:
    # 変数代入
    ctx = snowflake.connector.connect(
    user=sf_user,
    password=sf_password,
    account=sf_account,
    )
    cs = ctx.cursor()

except snowflake.connector.errors.DatabaseError:
    st.error("Snowflakeのアカウント名、ユーザー名、パスワードのいずれかが間違っています")

# (保存用)ユーザーによっては以下のクエリ実行必須
# cs.execute("use role " + sf_role)
# cs.execute("use warehouse " + sf_warehouse)

##################################################
# タイトル設定
##################################################
st.set_page_config(
    page_title="山手線アプリ",
    page_icon="🚉",
    layout="wide"
)
st.title("JR山手線 停車駅の一覧")
st.title(" ")

##################################################
# 関数
##################################################

###################################################
# 関数名：getMainData
#
# 機能概要：
# メインデータ取得
##################################################
# キャッシュ
@st.experimental_memo
def getMainData():
    data_result = cs.execute('''SELECT 
            STATION_NAME, 
            PASSENGERS,
            LONGITUDE_LATITUDE 
        FROM ''' 
        + main_table)

    # データフレーム作成
    data = pd.DataFrame(data_result, columns = ["駅名", "1日の平均乗降者数(人)", "緯度経度(GEOGRAPHY型)"])
    data.index = data.index + 1
    return data

###################################################
# 関数名：getDataframeData
#
# 機能概要：
# データフレームにカラムを追加
##################################################
# キャッシュ
@st.experimental_memo
def getDataframeData():
    # データフレームにカラム追加
    main_df = getMainData().assign(緯度 = 0, 経度 = 0) # 0はダミーデータ
    return main_df

###################################################
# 関数名：makeDataframe
#
# 機能概要：
# データフレーム作成
##################################################
# キャッシュ
@st.experimental_memo
def makeDataframe():
    main_df = getDataframeData()
    # 緯度と経度をGeography型オブジェクトから抽出しデータフレームに追加
    for index, row in main_df.iterrows():
        # 緯度
        latitude = cs.execute('''SELECT 
        st_y(
        SELECT 
            LONGITUDE_LATITUDE 
        FROM '''
        + main_table +
        '''WHERE STATION_NAME = \'''' + row['駅名'] + '''\')''').fetchall()

        # 経度
        longtitude = cs.execute('''SELECT 
        st_x(
        SELECT 
            LONGITUDE_LATITUDE 
        FROM  '''
        + main_table +
        '''WHERE STATION_NAME = \'''' + row['駅名'] + '''\')''').fetchall()   

        # listをstrに変更 
        y_str = str(latitude)[2:-3] 
        x_str = str(longtitude)[2:-3]
        # データフレームの列をfloatに指定
        main_df['緯度'] = main_df['緯度'].astype(float)
        main_df['経度'] = main_df['経度'].astype(float)
        # 追加した列にデータを挿入   
        main_df['緯度'][index] =  float(y_str) # Python 3.10.0以降ではfloat型への変換が必須
        main_df['経度'][index] =  float(x_str)
    return pd.DataFrame(main_df)

###################################################
# 関数名：getHeatData
#
# 機能概要：
# ヒートマップデータ取得
##################################################
# 注：キャッシュ機能使用不可
def getHeatData():

    # ヒートマップデータ作成
    heat_df = makeDataframe()[["緯度", "経度", "1日の平均乗降者数(人)"]]

    # マップの初期設定
    st.session_state["m"] = folium.Map(location=[35.69193, 139.736254], zoom_start=12) 

    # マップの値設定
    for i, row in makeDataframe().iterrows():
        # ポップアップの作成(駅名+緯度+経度+乗降者数)
        pop=f"{row['駅名']}<br>　緯度…{row['緯度']:,}<br>　経度…{row['経度']:,}<br>　1日の平均乗降者数…{row['1日の平均乗降者数(人)']:,}人"
        folium.Marker(
            # 緯度と経度を指定
            location=[row['緯度'], row['経度']],
            # ツールチップの指定(駅名)
            tooltip=row['駅名'],
            # ポップアップの指定
            popup=folium.Popup(pop, max_width=300),
            # アイコンの指定(アイコン、色)
            icon=folium.Icon(color="green")
        ).add_to(st.session_state["m"])

    # ヒートマップの作成
    folium.plugins.HeatMap(
        data = heat_df.values, # 2次元を渡す
        radius=25, 
        gradient={0.1: 'blue', 0.25: 'lime', 0.5:'yellow',0.75: 'red'},
    ).add_to(st.session_state["m"])

###################################################
# 関数名：dispSideBar 
#
# 機能概要：
# サイドバー作成
##################################################
def dispSideBar ():
    # タイトル表示
    st.sidebar.header("🚉駅間の距離を調べる")
    st.sidebar.subheader(" ")
    st.sidebar.subheader(" ")

    # 駅名取得
    erea_list = getMainData()["駅名"] # getMainData関数内から駅名取得

    # セレクトボックスを作成する
    selected_erea1 = st.sidebar.selectbox(
        ' 1つ目の駅を選択：',
        erea_list
    )
    selected_erea2 = st.sidebar.selectbox(
        '2つ目の駅を選択：',
        erea_list
    )
    st.sidebar.write(" ")

    # データ取得（地理空間関数(st_distance)使用)　# 都度データ取得が必須なため、キャッシュは使用しない
    distance_data = cs.execute('''SELECT ST_DISTANCE(
        (SELECT 
            LONGITUDE_LATITUDE
        FROM '''
        + main_table + 
        ''' WHERE STATION_NAME = \''''
        + selected_erea1 + 
        ''''), 
        (SELECT 
            LONGITUDE_LATITUDE 
        FROM '''
        + main_table +
        ''' WHERE STATION_NAME = \''''
        + selected_erea2 + 
        '''' )) 
        as DISTANCE_IN_MERTERS''').fetchall()

    # 距離表示
    if selected_erea1 != selected_erea2:
        st.sidebar.write("🗼距離:" + str(distance_data)[2:9] + "m")
    else:
        st.sidebar.write("🗼距離: 0m")

##################################################
# ツール実行
##################################################
## メイン画面
# 画面分割
col1, col2 = st.columns([1, 0.8])
with col1:
    # データフレーム表示
    st_df = st.dataframe(makeDataframe())
    # データフレーム型なので、変数への代入が必須
    if st_df == False:
        st.error("駅間の距離を取得できません")
        pass

with col2:
    # 画像表示
    st.image(image, use_column_width=False)
    st.write(" ")

# ヒートマップデータ取得
if getHeatData() == False:
    st.error("ヒートマップ情報を取得できません")
    pass

# マップ表示
st_data = st_folium(st.session_state["m"], width=1300, height=800)

# 運休情報リンク表示
st.markdown(link, unsafe_allow_html=True)

## サイドバー画面
if dispSideBar () == False:
    st.error("駅間の距離を取得できません")
    pass
