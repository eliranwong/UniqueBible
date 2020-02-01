import config

# Old files
oldFiles = (
    (config.marvelData, "collections.sqlite"),
    (config.marvelData, "collections2.sqlite"),
    (config.marvelData, "indexes.sqlite"),
    (config.marvelData, "data", "exlb.data")
    (config.marvelData, "data", "exlb2.data")
)

# A tulple of files which have been updated since the initial release
updatedFiles = ("CUV.bible", "CUVs.bible", "ULT.bible", "UST.bible", "SBLGNT.bible", "SBLGNTl.bible", "LXX1.bible", "LXX2.bible", "LXX1i.bible", "LXX2i.bible", "MOB.bible", "MPB.bible", "MIB.bible", "MAB.bible", "MTB.bible")
bibleInfo = {
    "ASV": ((config.marvelData, "bibles", "ASV.bible"), "1oDuV54_zOl_L0GQqmYiLvgjk2pQu4iSr", "American Standard Version"),
    "BSB": ((config.marvelData, "bibles", "BSB.bible"), "1fQX8cT12LE9Q3dBUJyezTYg4a0AbdKbN", "Berean Study Bible"),
    "CUV": ((config.marvelData, "bibles", "CUV.bible"), "1SuXGZIx_ivz9ztPvnylO_ComYOYrJyzk", "Chinese Union Version (Traditional Chinese)"),
    "CUVs": ((config.marvelData, "bibles", "CUVs.bible"), "1cu0FFIb_Zc3lQ71P1EJB3P8E5vDLnOt6", "Chinese Union Version (Simplified Chinese)"),
    "ISV": ((config.marvelData, "bibles", "ISV.bible"), "1_nmaakABx8wVsQHdBL9rVh2wtRK8uyyW", "International Standard Version"),
    "KJV": ((config.marvelData, "bibles", "KJV.bible"), "1ycOkEJ2JI_4iwjllb4mE02wkDvrsPlNq", "King James Version"),
    "LEB": ((config.marvelData, "bibles", "LEB.bible"), "1p-_phmh3y54i4FSLhzEd33_v0kzSjAZn", "Lexhame English Bible"),
    "LXX1": ((config.marvelData, "bibles", "LXX1.bible"), "1t9sgkQxYkZElg1M8f3QHYIF8oRAIN_hd", "Septuagint / LXX [main]"),
    "LXX1i": ((config.marvelData, "bibles", "LXX1i.bible"), "1vtGfv2otmb2N86M2QdRB6KdFjlNyAGOc", "Septuagint / LXX interlinear [main]"),
    "LXX2": ((config.marvelData, "bibles", "LXX2.bible"), "1oZk5nYKcR1s2XtRLfU-H9IxCkCQ2px6U", "Septuagint / LXX [alternate]"),
    "LXX2i": ((config.marvelData, "bibles", "LXX2i.bible"), "1jgq30khM0Oqxa3phE07Wg4R2p15t1N12", "Septuagint / LXX interlinear [alternate]"),
    "MAB": ((config.marvelData, "bibles", "MAB.bible"), "1E1W145QQOgm-_k3nkjvIFzRasIG9RL0C", "Marvel Annotated Bible"),
    "MIB": ((config.marvelData, "bibles", "MIB.bible"), "1AWr4F3GoqLs1pgOnQH6s0rJj_8frT9Ve", "Marvel Interlinear Bible"),
    "MOB": ((config.marvelData, "bibles", "MOB.bible"), "1EQyskcmH9eqIv-9SxoM2wPBgHWcuOEvc", "Marvel Original Bible"),
    "MPB": ((config.marvelData, "bibles", "MPB.bible"), "1hJYhu9E1odXNYBKrpUAjl_IvqWUVhHFm", "Marvel Parallel Bible"),
    "MTB": ((config.marvelData, "bibles", "MTB.bible"), "126VcL8UXwV4FJwO-ZQPZzNqEvrUALuDN", "Marvel Trilingual Bible"),
    "NET": ((config.marvelData, "bibles", "NET.bible"), "1pJ_9Wk4CmDdFO08wioOxs4krKjNeh4Ur", "New English Translation"),
    "SBLGNT": ((config.marvelData, "bibles", "SBLGNT.bible"), "1N1ryqvSytW3RFlOUy7rex0JdO2X5IzuK", "SBL Greek New Testament"),
    "SBLGNTl": ((config.marvelData, "bibles", "SBLGNTl.bible"), "1IgbX1ZBB05FgNglQM8t6GZBNSJVCu2fS", "SBL Greek New Testament annotated"),
    "ULT": ((config.marvelData, "bibles", "ULT.bible"), "1C_YiWs7GsduCuBOO4vSR7c13RRFtIZGg", "unfoldingWord Literal Text"),
    "UST": ((config.marvelData, "bibles", "UST.bible"), "1-s7NUKpPauer3w1hpu6W9YqVBjiLuXmc", "unfoldingWord Simplified Text"),
    "WEB": ((config.marvelData, "bibles", "WEB.bible"), "1L9qAeamdZwGzVdf7jC4_ks05hyQa2R7l", "World English Bible"),
}
