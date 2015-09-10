import logging
from web_util import *

__KEYS_DB__ = "db\\tagstats.db"
__VALUES_DB__ = "db\\tagstats_values.db"
__TAGINFO_DB__ = "db\\taginfo-db.db"

last_taginfo = []


def check_db():
    import sqlite3 as sql
    from datetime import date

    logger = logging.getLogger("tagStats.check_db")
    logger.info("Checking if new db")
    connection = sql.connect(__TAGINFO_DB__)
    c = connection.cursor()
    check_sql = '''SELECT update_end FROM source'''
    sql_data = c.execute(check_sql).fetchone()
    sql_date = sql_data[0][:10].split('-')
    logger.debug(sql_date)
    s_date = date(int(sql_date[0]), int(sql_date[1]), int(sql_date[2]))
    connection.close()

    # _db_info: name;taginfo_last;update_start;update_end
    connection = sql.connect(__KEYS_DB__)
    c = connection.cursor()
    check_db = '''SELECT taginfo_last FROM _db_info'''
    db_data = c.execute(check_db).fetchone()
    db_date = db_data[0][:10].split('-')
    logger.debug(db_date)
    d_date = date(int(db_date[0]), int(db_date[1]), int(db_date[2]))
    connection.close()

    if s_date == d_date:
        logger.info("Old db found! Exiting...")
        return False
    else:
        last_taginfo.append(sql_data[0])
        logger.debug(sql_data[0])
        logger.info("New db found!")
        return True


def update_info(last_ti, ts_start, ts_end):
    import sqlite3 as sql
    logger = logging.getLogger("tagStats.update_info")
    logger.info(
        "Updating with: {0}, {1}, {2}".format(last_ti, ts_start, ts_end))
    connection = sql.connect(__KEYS_DB__)
    c = connection.cursor()
    c.execute('''UPDATE _db_info SET taginfo_last="{0}",update_start="{1}",update_end="{2}" WHERE name="tagstats_db"'''.format(
        last_ti, ts_start, ts_end))
    connection.commit()
    connection.close()


def download_db():
    import urllib.request as urllib
    import os
    logger = logging.getLogger("tagStats.download_db")

    url = "http://taginfo.openstreetmap.org/download/taginfo-db.db.bz2"
    path = "db\\taginfo-db.db.bz2"
    logger.info("Download started @{0} to {1}".format(url, path))
    urllib.urlretrieve(url, path)
    logger.info("Extracting started")
    os.system("7z x {fname} -odb\\".format(fname=path))
    logger.info("Deleting file...")
    os.remove(path)
    logger.info("Download completed!")


def delete():
    import os
    os.remove(__TAGINFO_DB__)


def create_db(name, cursor, typ="KEY"):
    # note: c must be cursor,
    logger = logging.getLogger("tagStats.create_db")
    try:
        base = '''CREATE TABLE "{0}" (alles INTEGER, nodes INTEGER, ways INTEGER, relations INTEGER, used_by INTEGER, data INTEGER)'''
        vals = '''CREATE TABLE "{0}" (value TEXT, alles INTEGER, nodes INTEGER, ways INTEGER, relations INTEGER, data INTEGER)'''

        if typ == "KEY":
            logger.debug(
                "Trying to create db key entry using @{0}".format(base.format(name)))
            cursor.execute(base.format(name))
        elif typ == "VAL":
            logger.debug(
                "Trying to create db value entry using @{0}".format(vals.format(name)))
            cursor.execute(vals.format(name))
    except:
        logger.error("Error by using tag @{0}".format(name))
        print(
            "NAME BŁAAAAAAAAAAAAAAĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄAAD!....**$$#@@ WHEN {0}".format(name))


def nname():
    import sqlite3 as sql
    connection = sql.connect(__KEYS_DB__)
    c = connection.cursor()
    create_db("name", c)
    c.execute(
        '''CREATE TABLE _tag_names (fake_name TEXT, true_name TEXT, value_index INTEGER)''')
    connection.commit()
    connection.close()


def is_table(name, cursor):
    logger = logging.getLogger("tagStats.is_table")
    # note: c must be cursor
    find_anfrage = '''SELECT name FROM sqlite_master WHERE type='table' AND name="{0}"'''
    logger.debug("Checking or {0} exists".format(name))
    isit = cursor.execute(find_anfrage.format(name)).fetchall()
    if isit != []:
        return True
    else:
        return False

names = []  # fake,true


def change_name(name):
    import re
    logger = logging.getLogger("tagStats.change_name")

    tag_name = ""
    if (":" or "-") in name or name[0].isnumeric():
        nlist = re.split('\W+', name)

        for i in nlist:
            tag_name += i

        if name[0].isnumeric():
            if tag_name == "":
                tag_name = "_" + name
            else:
                tag_name = "_" + tag_name

        names.append((tag_name, name))
        # print(tag_name)
        logger.debug("Name {0} changed to {1}".format(name, tag_name))
        return tag_name
    else:
        logger.debug("Name {0} not changed".format(name))
        return name


all_keys = []
key_only = []
key_dont = []
import_data = []


def make_names_table():
    import sqlite3 as sql
    logger = logging.getLogger("tagStats.make_names_table")

    connection = sql.connect(__KEYS_DB__)
    c = connection.cursor()
    find_anfrage = '''SELECT true_name FROM _tag_names WHERE fake_name="{0}"'''
    for i in names:
        # print(i)
        # print(i[0])
        # print(find_anfrage.format(i[0]))
        logger.debug("Running command {0}".format(find_anfrage.format(i[0])))
        found = c.execute(find_anfrage.format(i[0])).fetchall()
        if found == []:
            add_data = '''INSERT INTO _tag_names VALUES {0}'''
            if i[1] in key_dont:
                i_n = (i[0], i[1], 1)
            else:
                i_n = (i[0], i[1], 0)
            c.execute(add_data.format(i_n))
            logger.debug("{0} added to name index".format(i[0]))

    connection.commit()
    connection.close()
    logger.info("Name index updated")


def find_all():
    import sqlite3 as sql
    logger = logging.getLogger("tagStats.find_all")

    connection = sql.connect(__TAGINFO_DB__)
    c = connection.cursor()

    fkeys = '''SELECT key FROM keys WHERE (count_all>=1000 AND NOT characters="letters") ORDER BY count_all DESC'''
    all_mkeys = c.execute(fkeys).fetchall()
    connection.close()
    for i in all_mkeys:
        all_keys.append(i[0])

    logger.info("Tag index created")

keys_filter = ["key", "turn", "direction", "owner", "minspeed", "collection_times", "levels", "garmin_type", "step_count", "min_height", "circumfere", "is_instate_code", "to", "from", "distance", "circumference", "comment",
               "divipola", "ntd_id", "hombre", "cmt", "tot_viv", "ponderado", "vulnerab_r", "mujer", "protect_class", "protection_title", "acres", "project", "official_status", "email", "nycdoittbin", "traffic_sign", "gauge", "frequency", "network", "surveydate", "est_width", "est_height", "est", "width", "height", "length", "incline", "fixme", "todo", "TODO", "FIXME", "website", "url", "uri", "voltage", "description", "inscription", "phone", "opening_hours", "postal_code"]
import_filter = ["created_by", "extensions", "attribution",
                 "gtfs_id", "arpav_codice_sottobacino", "istat_id"]


def sort():
    logger = logging.getLogger("tagStats.sort")
    for i in all_keys:
        if i.startswith("_") or i.endswith("_") or i.startswith("iemv") or i.startswith("converted_by") or i.startswith("cesena:") or i.startswith("teryt") or i.startswith("gns:") or i.startswith("USGS-LULC:") or i.startswith("unocha:") or i.startswith("gtfs:") or i.startswith("gvr:") or i.startswith("sby:") or i.startswith("rednap:") or i.startswith("maaamet:") or i.startswith("paloalto_ca:") or i.startswith("us.fo:") or i.startswith("geobase:") or i.startswith("kvl_hro:") or i.startswith("okato:") or i.startswith("siruta:") or i.startswith("idp:") or i.startswith("redwood_city_ca:") or i.startswith("metcouncil:") or i.startswith("cxx:") or i.startswith("nvdb:") or i.startswith("fdot:") or i.startswith("catmp-RoadID") or i.startswith("ts_") or i.startswith("nga:") or i.startswith("IBGE:") or i.startswith("bbg:") or i.startswith("4C:") or i.startswith("opendata:") or i.startswith("mhs:") or i.startswith("strassen-nrw:") or i.startswith("qroti:") or i.startswith("vrr:") or i.startswith("cadastre:") or i.startswith("emuia:") or i.startswith("no-kartverket-ssr:") or i.startswith("catastro:") or i.startswith("nist:") or i.startswith("eea:") or i.startswith("gps:") or i.startswith("pre-CLC:") or i.startswith("pe:") or i.startswith("fi:") or i.startswith("OGD-Stmk:") or i.startswith("oa:") or i.startswith("NYSTL:") or i.startswith("educamadrid:") or i.startswith("brt:") or i.startswith("usar_addr:") or i.startswith("dibavod:") or i.startswith("massgis:") or i.startswith("NHD:") or i.startswith("dcgis:") or i.startswith("raba:") or i.startswith("adr_les") or i.startswith("bag:") or i.startswith("cladr:") or i.startswith("bmo:") or i.startswith("surrey:") or i.startswith("rer_edi_id:") or i.startswith("ewmapa:") or i.startswith("uuid:") or i.startswith("mml:") or i.startswith("kms:") or i.startswith("lbcs:") or i.startswith("dcgis:") or i.startswith("clc:") or i.startswith("nhd-shp:") or i.startswith("tiger:") or i.startswith("mvdgis:") or i.startswith("osak:") or i.startswith("nhd:") or i.startswith("gnis:") or i.startswith("it:") or i.startswith("lojic:") or i.startswith("gst:") or i.startswith("ngbe:"):
            import_data.append(i)
        elif i in import_filter:
            import_data.append(i)
        elif i.startswith("turn:lanes") or i.endswith("count") or i.startswith("placement") or i.startswith("overtaking") or i.startswith("ncat") or i.startswith("object:") or i.startswith("change") or i.startswith("chile") or i.startswith("capacity") or i.startswith("ref") or i.startswith("accuracy") or i.startswith("taxon") or i.startswith("genus") or i.startswith("species") or i.startswith("is_in") or i.startswith("title") or i.endswith("title") or i.startswith("zip") or i.startswith("retrieved") or i.startswith("diameter") or i.endswith("survey") or i.startswith("survey") or i.startswith("population") or i.endswith("simc") or i.endswith("date") or i.startswith("operator") or i.endswith("operator") or i.startswith("import") or i.endswith("ref") or i.startswith("note") or i.startswith("addr") or i.startswith("contact") or i.startswith("wikipedia") or i.startswith("ele") or i.endswith(":lanes") or i.startswith("lanes") or i.startswith("roof:") or i.startswith("building:") or i.startswith("source") or i.startswith("max") or i.endswith("name") or i.startswith("name"):
            key_only.append(i)
        elif i in keys_filter:
            key_only.append(i)
        else:
            key_dont.append(i)

    logger.info("Tag index sorted")


def update_datasets(tag_name, apply_values=False, values_limit=500):
    from time import localtime, strftime
    import sqlite3 as sql
    logger = logging.getLogger("tagStats.update_datasets")

    ####TAGINFO DB####
    connection = sql.connect(__TAGINFO_DB__)
    c = connection.cursor()

    keys_anfrage = '''SELECT count_all,count_nodes,count_ways,count_relations,users_all FROM keys WHERE key="{0}"'''
    values_anfrage = '''SELECT value,count_all,count_nodes,count_ways,count_relations FROM tags WHERE (key="{0}" AND count_all>{1}) ORDER BY count_all DESC'''
    logger.debug(keys_anfrage.format(tag_name))
    tag_key = c.execute(
        keys_anfrage.format(tag_name)).fetchall()  # list of tuples

    if apply_values == True:
        logger.debug(values_anfrage.format(tag_name, str(values_limit)))
        tag_val = c.execute(
            values_anfrage.format(tag_name, str(values_limit))).fetchall()  # list of tuples

    connection.close()

    tag_name = change_name(tag_name)

    ####MY DB####
    n_connection = sql.connect(__KEYS_DB__)
    c = n_connection.cursor()

    if tag_key == []:
        logger.error("Error by using tag {0}".format(tag_name))
        print("NIEOCZEKIWANY BŁĄD WYKONANIA....PRZY TAGU {0}".format(tag_name))
        return None
    else:
        timek = int(strftime("%Y%m%d", localtime()))
        # timek = 20150819
        new_key = list(tag_key[0])
        new_key.append(timek)

    if is_table(tag_name, c) == False:
        create_db(tag_name, c)
    else:
        pass

    add_data = '''INSERT INTO "{0}" VALUES {1}'''
    logger.debug(add_data.format(tag_name, tuple(new_key)))
    c.execute(add_data.format(tag_name, tuple(new_key)))
    logger.info("Updated ===== {0} ===== KEY record".format(tag_name))

    n_connection.commit()
    n_connection.close()
    try:
        if apply_values == True:
            v_connection = sql.connect(__VALUES_DB__)
            c = v_connection.cursor()

            if is_table(tag_name, c) == False:
                create_db(tag_name, c, "VAL")
            else:
                pass

            for i in tag_val:
                val_list = list(i)
                val = val_list[0]
                val_list.append(timek)
                val_tuple = tuple(val_list)

                logger.debug(add_data.format(tag_name, val_tuple))
                c.execute(add_data.format(tag_name, val_tuple))
                logger.info("Updated {0} VALUE record".format(val))

            v_connection.commit()
            v_connection.close()
    except:
        logger.error(
            "Error by using tag {0} by value {1}".format(tag_name, val))
        print("BŁĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄAD!......$$##^^&& WHEN {0}".format(
            tag_name))

        # stwurz i tub update_datasets

        # is_it = c.execute(find_anfrage.format(val)).fetchall()
        # if is_it != []:
        #     c.execute(add_data.format(val, val_tuple))
        #     print("Added {0}".format(val))
        # else:
        #     c.execute(make_table.format(val))
        #     c.execute(add_data.format(val, val_tuple))
        #     print("Added {0}".format(val))


def main_db():
    from time import localtime, strftime
    logger = logging.getLogger("tagStats")
    logger.setLevel(logging.INFO)

    log_date = strftime("%d%m", localtime())
    fh = logging.FileHandler(
        "logs\\tagstats{0}.log".format(log_date), 'w', 'utf-8', False)
    form = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(form)

    logger.addHandler(fh)
    logger.info("TagStats v.0.9 -- Javnik -- data from TagInfo")
    st_date = strftime("%Y-%m-%d %H:%M:%S", localtime())
    download_db()
    c = check_db()
    if c == True:
        find_all()
        sort()
        # nname()

        for i in key_only:
            if i in ["to", "from"]:  # work at it
                pass
            else:
                update_datasets(i)
                make_tag_html(i, False)

        print("Key_only datasets updated.")
        for i in key_dont:
            if i == "area:highway":
                update_datasets(i, True, 50)
                make_tag_html(i, True)
            else:
                update_datasets(i, True)
                make_tag_html(i, True)
        print("Value datasets updated.")
        make_names_table()

    logger.info("Deleting taginfo-db...")
    delete()
    make_tags_list_html()
    end_date = strftime("%Y-%m-%d %H:%M:%S", localtime())
    update_info(last_taginfo[0], st_date, end_date)

    logger.info("End of execution.")
    logger.info("----------------------------------------------------")
