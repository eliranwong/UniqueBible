from uniquebible import config


class DatafileLocation:
    marvelBibles = {
        "ASV": (
            (config.marvelData, "bibles", "ASV.bible"), "1oDuV54_zOl_L0GQqmYiLvgjk2pQu4iSr", "American Standard Version"),
        "BSB": ((config.marvelData, "bibles", "BSB.bible"), "1fQX8cT12LE9Q3dBUJyezTYg4a0AbdKbN", "Berean Study Bible"),
        "CUV": ((config.marvelData, "bibles", "CUV.bible"), "1SuXGZIx_ivz9ztPvnylO_ComYOYrJyzk",
                "Chinese Union Version (Traditional Chinese)"),
        "CUVs": ((config.marvelData, "bibles", "CUVs.bible"), "1cu0FFIb_Zc3lQ71P1EJB3P8E5vDLnOt6",
                 "Chinese Union Version (Simplified Chinese)"),
        "ISV": ((config.marvelData, "bibles", "ISV.bible"), "1_nmaakABx8wVsQHdBL9rVh2wtRK8uyyW",
                "International Standard Version"),
        "KJV": ((config.marvelData, "bibles", "KJV.bible"), "1ycOkEJ2JI_4iwjllb4mE02wkDvrsPlNq", "King James Version"),
        "LEB": (
            (config.marvelData, "bibles", "LEB.bible"), "1p-_phmh3y54i4FSLhzEd33_v0kzSjAZn", "Lexhame English Bible"),
        "LXX1": (
            (config.marvelData, "bibles", "LXX1.bible"), "1t9sgkQxYkZElg1M8f3QHYIF8oRAIN_hd", "Septuagint / LXX [main]"),
        "LXX1i": ((config.marvelData, "bibles", "LXX1i.bible"), "1vtGfv2otmb2N86M2QdRB6KdFjlNyAGOc",
                  "Septuagint / LXX interlinear [main]"),
        "LXX2": ((config.marvelData, "bibles", "LXX2.bible"), "1oZk5nYKcR1s2XtRLfU-H9IxCkCQ2px6U",
                 "Septuagint / LXX [alternate]"),
        "LXX2i": ((config.marvelData, "bibles", "LXX2i.bible"), "1jgq30khM0Oqxa3phE07Wg4R2p15t1N12",
                  "Septuagint / LXX interlinear [alternate]"),
        "MAB": (
            (config.marvelData, "bibles", "MAB.bible"), "1E1W145QQOgm-_k3nkjvIFzRasIG9RL0C", "Marvel Annotated Bible"),
        "MIB": (
            (config.marvelData, "bibles", "MIB.bible"), "1AWr4F3GoqLs1pgOnQH6s0rJj_8frT9Ve", "Marvel Interlinear Bible"),
        "MOB": (
            (config.marvelData, "bibles", "MOB.bible"), "1EQyskcmH9eqIv-9SxoM2wPBgHWcuOEvc", "Marvel Original Bible"),
        "MPB": (
            (config.marvelData, "bibles", "MPB.bible"), "1hJYhu9E1odXNYBKrpUAjl_IvqWUVhHFm", "Marvel Parallel Bible"),
        "MTB": (
            (config.marvelData, "bibles", "MTB.bible"), "126VcL8UXwV4FJwO-ZQPZzNqEvrUALuDN", "Marvel Trilingual Bible"),
        "NET": (
            (config.marvelData, "bibles", "NET.bible"), "1pJ_9Wk4CmDdFO08wioOxs4krKjNeh4Ur", "New English Translation"),
        "SBLGNT": (
            (config.marvelData, "bibles", "SBLGNT.bible"), "1N1ryqvSytW3RFlOUy7rex0JdO2X5IzuK", "SBL Greek New Testament"),
        "SBLGNTl": ((config.marvelData, "bibles", "SBLGNTl.bible"), "1IgbX1ZBB05FgNglQM8t6GZBNSJVCu2fS",
                    "SBL Greek New Testament annotated"),
        "ULT": (
            (config.marvelData, "bibles", "ULT.bible"), "1C_YiWs7GsduCuBOO4vSR7c13RRFtIZGg", "unfoldingWord Literal Text"),
        "UST": ((config.marvelData, "bibles", "UST.bible"), "1-s7NUKpPauer3w1hpu6W9YqVBjiLuXmc",
                "unfoldingWord Simplified Text"),
        "WEB": ((config.marvelData, "bibles", "WEB.bible"), "1L9qAeamdZwGzVdf7jC4_ks05hyQa2R7l", "World English Bible"),
    }

    marvelCommentaries = {
        "Notes on the Old and New Testaments (Barnes) [26 vol.]": (
            (config.marvelData, "commentaries", "cBarnes.commentary"), "13uxButnFH2NRUV-YuyRZYCeh1GzWqO5J"),
        "Commentary on the Old and New Testaments (Benson) [5 vol.]": (
            (config.marvelData, "commentaries", "cBenson.commentary"), "1MSRUHGDilogk7_iZHVH5GWkPyf8edgjr"),
        "Biblical Illustrator (Exell) [58 vol.]": (
            (config.marvelData, "commentaries", "cBI.commentary"), "1DUATP_0M7SwBqsjf20YvUDblg3_sOt2F"),
        "Complete Summary of the Bible (Brooks) [2 vol.]": (
            (config.marvelData, "commentaries", "cBrooks.commentary"), "1pZNRYE6LqnmfjUem4Wb_U9mZ7doREYUm"),
        "John Calvin's Commentaries (Calvin) [22 vol.]": (
            (config.marvelData, "commentaries", "cCalvin.commentary"), "1FUZGK9n54aXvqMAi3-2OZDtRSz9iZh-j"),
        "Cambridge Bible for Schools and Colleges (Cambridge) [57 vol.]": (
            (config.marvelData, "commentaries", "cCBSC.commentary"), "1IxbscuAMZg6gQIjzMlVkLtJNDQ7IzTh6"),
        "Critical And Exegetical Commentary on the NT (Meyer) [20 vol.]": (
            (config.marvelData, "commentaries", "cCECNT.commentary"), "1MpBx7z6xyJYISpW_7Dq-Uwv0rP8_Mi-r"),
        "Cambridge Greek Testament for Schools and Colleges (Cambridge) [21 vol.]": (
            (config.marvelData, "commentaries", "cCGrk.commentary"), "1Jf51O0R911Il0V_SlacLQDNPaRjumsbD"),
        "Church Pulpit Commentary (Nisbet) [12 vol.]": (
            (config.marvelData, "commentaries", "cCHP.commentary"), "1dygf2mz6KN_ryDziNJEu47-OhH8jK_ff"),
        "Commentary on the Bible (Clarke) [6 vol.]": (
            (config.marvelData, "commentaries", "cClarke.commentary"), "1ZVpLAnlSmBaT10e5O7pljfziLUpyU4Dq"),
        "College Press Bible Study Textbook Series (College) [59 vol.]": (
            (config.marvelData, "commentaries", "cCPBST.commentary"), "14zueTf0ioI-AKRo_8GK8PDRKael_kB1U"),
        "Expositor's Bible Commentary (Nicoll) [49 vol.]": (
            (config.marvelData, "commentaries", "cEBC.commentary"), "1UA3tdZtIKQEx-xmXtM_SO1k8S8DKYm6r"),
        "Commentary for English Readers (Ellicott) [8 vol.]": (
            (config.marvelData, "commentaries", "cECER.commentary"), "1sCJc5xuxqDDlmgSn2SFWTRbXnHSKXeh_"),
        "Expositor's Greek New Testament (Nicoll) [5 vol.]": (
            (config.marvelData, "commentaries", "cEGNT.commentary"), "1ZvbWnuy2wwllt-s56FUfB2bS2_rZoiPx"),
        "Greek Testament Commentary (Alford) [4 vol.]": (
            (config.marvelData, "commentaries", "cGCT.commentary"), "1vK53UO2rggdcfcDjH6mWXAdYti4UbzUt"),
        "Exposition of the Entire Bible (Gill) [9 vol.]": (
            (config.marvelData, "commentaries", "cGill.commentary"), "1O5jnHLsmoobkCypy9zJC-Sw_Ob-3pQ2t"),
        "Exposition of the Old and New Testaments (Henry) [6 vol.]": (
            (config.marvelData, "commentaries", "cHenry.commentary"), "1m-8cM8uZPN-fLVcC-a9mhL3VXoYJ5Ku9"),
        "Horæ Homileticæ (Simeon) [21 vol.]": (
            (config.marvelData, "commentaries", "cHH.commentary"), "1RwKN1igd1RbN7phiJDiLPhqLXdgOR0Ms"),
        "International Critical Commentary, NT (1896-1929) [16 vol.]": (
            (config.marvelData, "commentaries", "cICCNT.commentary"), "1QxrzeeZYc0-GNwqwdDe91H4j1hGSOG6t"),
        "Jamieson, Fausset, and Brown Commentary (JFB) [6 vol.]": (
            (config.marvelData, "commentaries", "cJFB.commentary"), "1NT02QxoLeY3Cj0uA_5142P5s64RkRlpO"),
        "Commentary on the Old Testament (Keil & Delitzsch) [10 vol.]": (
            (config.marvelData, "commentaries", "cKD.commentary"), "1rFFDrdDMjImEwXkHkbh7-vX3g4kKUuGV"),
        "Commentary on the Holy Scriptures: Critical, Doctrinal, and Homiletical (Lange) [25 vol.]": (
            (config.marvelData, "commentaries", "cLange.commentary"), "1_PrTT71aQN5LJhbwabx-kjrA0vg-nvYY"),
        "Expositions of Holy Scripture (MacLaren) [32 vol.]": (
            (config.marvelData, "commentaries", "cMacL.commentary"), "1p32F9MmQ2wigtUMdCU-biSrRZWrFLWJR"),
        "Preacher's Complete Homiletical Commentary (Exell) [37 vol.]": (
            (config.marvelData, "commentaries", "cPHC.commentary"), "1xTkY_YFyasN7Ks9me3uED1HpQnuYI8BW"),
        "Pulpit Commentary (Spence) [23 vol.]": (
            (config.marvelData, "commentaries", "cPulpit.commentary"), "1briSh0oDhUX7QnW1g9oM3c4VWiThkWBG"),
        "Word Pictures in the New Testament (Robertson) [6 vol.]": (
            (config.marvelData, "commentaries", "cRob.commentary"), "17VfPe4wsnEzSbxL5Madcyi_ubu3iYVkx"),
        "Spurgeon's Expositions on the Bible (Spurgeon) [3 vol.]": (
            (config.marvelData, "commentaries", "cSpur.commentary"), "1OVsqgHVAc_9wJBCcz6PjsNK5v9GfeNwp"),
        "Word Studies in the New Testament (Vincent) [4 vol.]": (
            (config.marvelData, "commentaries", "cVincent.commentary"), "1ZZNnCo5cSfUzjdEaEvZ8TcbYa4OKUsox"),
        "John Wesley's Notes on the Whole Bible (Wesley) [3 vol.]": (
            (config.marvelData, "commentaries", "cWesley.commentary"), "1rerXER1ZDn4e1uuavgFDaPDYus1V-tS5"),
        "Commentary on the Old and New Testaments (Whedon) [14 vol.]": (
            (config.marvelData, "commentaries", "cWhedon.commentary"), "1FPJUJOKodFKG8wsNAvcLLc75QbM5WO-9"),
    }

    marvelData = {
        "Core Datasets": ((config.marvelData, "images.sqlite"), "1-aFEfnSiZSIjEPUQ2VIM75I4YRGIcy5-"),
        "Search Engine": ((config.marvelData, "search.sqlite"), "1A4s8ewpxayrVXamiva2l1y1AinAcIKAh"),
        "Smart Indexes": ((config.marvelData, "indexes2.sqlite"), "1hY-QkBWQ8UpkeqM8lkB6q_FbaneU_Tg5"),
        "Chapter & Verse Notes": ((config.marvelData, "note.sqlite"), "1OcHrAXLS-OLDG5Q7br6mt2WYCedk8lnW"),
        "Bible Topics Data": ((config.marvelData, "data", "exlb3.data"), "1gp2Unsab85Se-IB_tmvVZQ3JKGvXLyMP"),
        "Cross-reference Data": (
            (config.marvelData, "cross-reference.sqlite"), "1fTf0L7l1k_o1Edt4KUDOzg5LGHtBS3w_"),
        "Collections": ((config.marvelData, "collections3.sqlite"), "18dRwEc3SL2Z6JxD1eI1Jm07oIpt9i205"),
        "Dictionaries": ((config.marvelData, "data", "dictionary.data"), "1NfbkhaR-dtmT1_Aue34KypR3mfPtqCZn"),
        "Encyclopedia": ((config.marvelData, "data", "encyclopedia.data"), "1OuM6WxKfInDBULkzZDZFryUkU1BFtym8"),
        "Lexicons": ((config.marvelData, "lexicons", "MCGED.lexicon"), "157Le0xw2ovuoF2v9Bf6qeck0o15RGfMM"),
        "Atlas, Timelines & Books": (
            (config.marvelData, "books", "Maps_ABS.book"), "13hf1NvhAjNXmRQn-Cpq4hY0E2XbEfmEd"),
        "Word Data": ((config.marvelData, "data", "wordNT.data"), "11pmVhecYEtklcB4fLjNP52eL9pkytFdS"),
        "Words Data": ((config.marvelData, "data", "wordsNT.data"), "11bANQQhH6acVujDXiPI4JuaenTFYTkZA"),
        "Clause Data": ((config.marvelData, "data", "clauseNT.data"), "11pmVhecYEtklcB4fLjNP52eL9pkytFdS"),
        "Translation Data": (
            (config.marvelData, "data", "translationNT.data"), "11bANQQhH6acVujDXiPI4JuaenTFYTkZA"),
        "Discourse Data": ((config.marvelData, "data", "discourseNT.data"), "11bANQQhH6acVujDXiPI4JuaenTFYTkZA"),
        "TDW Combo Data": ((config.marvelData, "data", "wordsNT.data"), "11bANQQhH6acVujDXiPI4JuaenTFYTkZA"),
    }

#if __name__ == "__main__":
#    import os
#    from uniquebible import config
#
#    def installResources(resources):
#        count = 0
#        ids = []
#        for value in resources.values():
#            cloudID = value[1]
#            cloudFile = "https://drive.google.com/uc?id={0}".format(cloudID)
#            # e.g. "https://drive.google.com/uc?id=1UA3tdZtIKQEx-xmXtM_SO1k8S8DKYm6r"
#            # cli = "gdown {0} -O {1}.zip".format(cloudFile, cloudID)
#            try:
#                # os.system(cli)
#                count += 1
#                if not cloudID in ids:
#                    ids.append(cloudID)
#                else:
#                    print("Duplicated: {0}".format(cloudID))
#                if not os.path.exists("/home/e/development/uniquebibleapp-webtop/root/defaults/uba/{0}.zip".format(cloudID)):
#                    print("Not downloaded: {0}".format(cloudID))
#            except:
#                *_, filename = value[0]
#                print("Failed to download {0}!".format(filename))
#        print(count)
#
#    data = DatafileLocation()
#    for resources in (data.marvelBibles, data.marvelCommentaries, data.marvelData):
#        installResources(resources)
