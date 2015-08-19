# import os
# bdir = "E:\\Git\\TagsStats"


def download_db():
    import urllib.request as urllib
    import os

    url = "http://taginfo.openstreetmap.org/download/taginfo-db.db.bz2"
    path = "db\\taginfo-db.db.bz2"
    urllib.urlretrieve(url, path)

    os.system("7z x {fname} -odb\\".format(fname=path))
    os.remove(path)


def create_db(name, cursor, typ="KEY"):
    # note: c must be cursor
    try:
        base = '''CREATE TABLE "{0}" (alles INTEGER, nodes INTEGER, ways INTEGER, relations INTEGER, used_by INTEGER, data INTEGER)'''
        vals = '''CREATE TABLE "{0}" (value TEXT, alles INTEGER, nodes INTEGER, ways INTEGER, relations INTEGER, data INTEGER)'''

        if typ == "KEY":
            cursor.execute(base.format(name))
        elif typ == "VAL":
            cursor.execute(vals.format(name))
    except:
        print("NAME BŁAAAAAAAAAAAAAAĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄAAD!....**$$#@@")
        print(name)


def nname():
    import sqlite3 as sql
    connection = sql.connect("db\\tagstats.db")
    c = connection.cursor()
    create_db("name", c)
    c.execute(
        '''CREATE TABLE _tag_names (fake_name TEXT, true_name TEXT, value_index INTEGER)''')
    connection.commit()
    connection.close()


def is_table(name, cursor):
    # note: c must be cursor
    find_anfrage = '''SELECT name FROM sqlite_master WHERE type='table' AND name="{0}"'''
    isit = cursor.execute(find_anfrage.format(name)).fetchall()
    if isit != []:
        return True
    else:
        return False

names = []  # fake,true


def change_name(name):
    import re
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
        return tag_name
    else:
        return name


all_keys = []
key_only = []
key_dont = []
import_data = []


def make_names_table():
    import sqlite3 as sql

    connection = sql.connect("db\\tagstats.db")
    c = connection.cursor()
    find_anfrage = '''SELECT true_name FROM _tag_names WHERE fake_name="{0}"'''
    for i in names:
        # print(i)
        # print(i[0])
        # print(find_anfrage.format(i[0]))
        found = c.execute(find_anfrage.format(i[0])).fetchall()
        if found == []:
            add_data = '''INSERT INTO _tag_names VALUES {0}'''
            if i[1] in key_dont:
                i_n = (i[0], i[1], 1)
            else:
                i_n = (i[0], i[1], 0)
            c.execute(add_data.format(i_n))

    connection.commit()
    connection.close()
    print("Name index updated.")


def find_all():
    import sqlite3 as sql

    connection = sql.connect("db\\taginfo-db.db")
    c = connection.cursor()

    fkeys = '''SELECT key FROM keys WHERE (count_all>=1000 AND NOT characters="letters") ORDER BY count_all DESC'''
    all_mkeys = c.execute(fkeys).fetchall()
    connection.close()
    for i in all_mkeys:
        all_keys.append(i[0])

    print("Tag index created.")


def sort():
    for i in all_keys:
        if i.startswith("_") or i.endswith("_") or i.startswith("cesena:") or i.startswith("teryt") or i.startswith("gns:") or i.startswith("USGS-LULC:") or i.startswith("unocha:") or i.startswith("gtfs:") or i.startswith("gvr:") or i.startswith("sby:") or i.startswith("rednap:") or i.startswith("maaamet:") or i.startswith("paloalto_ca:") or i.startswith("us.fo:") or i.startswith("geobase:") or i.startswith("kvl_hro:") or i.startswith("okato:") or i.startswith("siruta:") or i.startswith("idp:") or i.startswith("redwood_city_ca:") or i.startswith("metcouncil:") or i.startswith("cxx:") or i.startswith("nvdb:") or i.startswith("fdot:") or i.startswith("catmp-RoadID") or i.startswith("ts_") or i.startswith("nga:") or i.startswith("IBGE:") or i.startswith("bbg:") or i.startswith("4C:") or i.startswith("opendata:") or i.startswith("mhs:") or i.startswith("strassen-nrw:") or i.startswith("qroti:") or i.startswith("vrr:") or i.startswith("cadastre:") or i.startswith("emuia:") or i.startswith("no-kartverket-ssr:") or i.startswith("catastro:") or i.startswith("nist:") or i.startswith("eea:") or i.startswith("gps:") or i.startswith("pre-CLC:") or i.startswith("pe:") or i.startswith("fi:") or i.startswith("OGD-Stmk:") or i.startswith("oa:") or i.startswith("NYSTL:") or i.startswith("educamadrid:") or i.startswith("brt:") or i.startswith("usar_addr:") or i.startswith("dibavod:") or i.startswith("massgis:") or i.startswith("NHD:") or i.startswith("dcgis:") or i.startswith("raba:") or i.startswith("adr_les") or i.startswith("bag:") or i.startswith("cladr:") or i.startswith("bmo:") or i.startswith("surrey:") or i.startswith("rer_edi_id:") or i.startswith("ewmapa:") or i.startswith("uuid:") or i.startswith("mml:") or i.startswith("kms:") or i.startswith("lbcs:") or i.startswith("dcgis:") or i.startswith("clc:") or i.startswith("nhd-shp:") or i.startswith("tiger:") or i.startswith("mvdgis:") or i.startswith("osak:") or i.startswith("nhd:") or i.startswith("gnis:") or i.startswith("it:") or i.startswith("lojic:") or i.startswith("gst:") or i.startswith("ngbe:"):
            import_data.append(i)
        elif i in ["created_by", "attribution", "gtfs_id"]:
            import_data.append(i)
        elif i.startswith("ref") or i.startswith("is_in") or i.startswith("title") i.endswith("title") or i.startswith("zip") or i.startswith("retrieved") or i.startswith("diameter") or i.startswith("survey") or i.startswith("population") or i.endswith("simc") or i.endswith("date") or i.startswith("operator") or i.endswith("operator") or i.startswith("import") or i.endswith("ref") or i.startswith("note") or i.startswith("addr") or i.startswith("contact") or i.startswith("wikipedia") or i.startswith("ele") or i.endswith(":lanes") or i.startswith("lanes") or i.startswith("roof:") or i.startswith("building:") or i.startswith("source") or i.startswith("max") or i.endswith("name") or i.startswith("name"):
            key_only.append(i)
        elif i in ["turn", "direction", "owner", "minspeed", "placement", "collection_times", "levels", "garmin_type", "step_count", "min_height", "circumfere", "is_instate_code", "to", "from", "distance", "circumference", "comment", "capacity", "surveydate", "est_width", "est_height", "est", "width", "height", "length", "incline", "fixme", "todo", "TODO", "FIXME", "website", "url", "uri", "voltage", "description", "inscription", "phone", "opening_hours", "postal_code"]:
            key_only.append(i)
        else:
            key_dont.append(i)

    print("Tag index sorted.")


def update_datasets(tag_name, apply_values=False, values_limit=500):
    from time import localtime, strftime
    import sqlite3 as sql

    ####TAGINFO DB####
    connection = sql.connect("db\\taginfo-db.db")
    c = connection.cursor()

    keys_anfrage = '''SELECT count_all,count_nodes,count_ways,count_relations,users_all FROM keys WHERE key="{0}"'''
    values_anfrage = '''SELECT value,count_all,count_nodes,count_ways,count_relations FROM tags WHERE (key="{0}" AND count_all>{1}) ORDER BY count_all DESC'''
    # print(keys_anfrage.format(tag_name))
    tag_key = c.execute(
        keys_anfrage.format(tag_name)).fetchall()  # list of tuples

    if apply_values == True:
        tag_val = c.execute(
            values_anfrage.format(tag_name, str(values_limit))).fetchall()  # list of tuples

    connection.close()

    tag_name = change_name(tag_name)

    ####MY DB####
    n_connection = sql.connect("db\\tagstats.db")
    c = n_connection.cursor()

    if tag_key == []:
        print("NIEOCZEKIWANY BŁĄD WYKONANIA....PRZY TAGU {0}".format(tag_name))
        return None
    else:
        timek = int(strftime("%Y%m%d", localtime()))
        new_key = list(tag_key[0])
        new_key.append(timek)

    if is_table(tag_name, c) == False:
        create_db(tag_name, c)
    else:
        pass

    add_data = '''INSERT INTO "{0}" VALUES {1}'''
    # print(add_data.format(tag_name, tuple(new_key)))
    c.execute(add_data.format(tag_name, tuple(new_key)))
    print("Updated {0} KEY record".format(tag_name))

    n_connection.commit()
    n_connection.close()
    try:
        if apply_values == True:
            v_connection = sql.connect("db\\tagstats_values.db")
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

                # print(add_data.format(tag_name, val_tuple))
                c.execute(add_data.format(tag_name, val_tuple))
                print("Updated {0} VALUE record".format(val))

            v_connection.commit()
            v_connection.close()
    except:
        print("BŁĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄĄAD!......$$##^^&&")
        print(tag_name)

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
    find_all()
    sort()
    # nname()

    for i in key_only:
        # print(i)
        if i in ["to", "from"]:  # work at it
            pass
        else:
            update_datasets(i)

    print("Key_only datasets updated.")
    for i in key_dont:
        # print(i)
        if i == "area:highway":
            update_datasets(i, True, 50)
        else:
            update_datasets(i, True)
    print("Value datasets updated.")
    make_names_table()


def make_graphs(tag_name, values=False):
    import sqlite3 as sql
    import pylab as p

    tag_name = change_name(tag_name)

    connection = sql.connect("db\\tagstats.db")
    c = connection.cursor()

    base = '''SELECT alles,nodes,ways,relations,used_by,data FROM {0} ORDER BY data ASC'''
    vals = '''SELECT value,alles,nodes,ways,relations,data FROM {0} ORDER BY data ASC'''

    key_db = c.execute(base.format(tag_name)).fetchall()
    # list of tuple [(1,2,3), (1,2,3) ]
    alles = []
    n = []
    w = []
    r = []
    u = []
    d = []

    for i in key_db:
        alles.append(i[0])
        n.append(i[1])
        w.append(i[2])
        r.append(i[3])
        u.append(i[4])
        d.append(i[5])

    p.figure(figsize=(10, 10), dpi=200)
    p.plot(d, alles, color="blue", label="all")
    p.plot(d, n, color="red", label="node")
    p.plot(d, w, color="green", label="way")
    p.plot(d, r, color="orange", label="relation")
    p.plot(d, r, color="black", label="used_by")
    # p.ylim(100, 50000)
    p.legend(loc="upper left")
    p.show()

    if values == True:
        tag_v = tag_name + "_values"
        val_db = c.execute(vals.format(tag_v)).fetchall()
        v = []
        alles.clear()
        n.clear()
        w.clear()
        r.clear()
        d.clear()

        # NOT SO EASY!
        for i in val_db:
            v.append(i[0])
            alles.append(i[1])
            n.append(i[2])
            w.append(i[3])
            r.append(i[4])
            d.append(i[5])

            p.figure(figsize=(10, 10), dpi=200)
            p.title("value")
            p.plot(d, alles, color="blue", label="all")
            p.plot(d, n, color="red", label="node")
            p.plot(d, w, color="green", label="way")
            p.plot(d, r, color="orange", label="relation")
            # p.ylim(100, 50000)
            p.legend(loc="upper left")
            p.show()
