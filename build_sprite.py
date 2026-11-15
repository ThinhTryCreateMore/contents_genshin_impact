import os
import re
import math
import json
import requests
from io import BytesIO
from PIL import Image, UnidentifiedImageError

null = None
true = True
false = False

# Dán kết quả copy từ ô characters_data vào thay thế mảng bên dưới
CHARACTERS = [
   {"name":"Aino","url":"https://lh3.google.com/u/0/d/1IM7WLiBIlyGpr4SMU-6D1r_R7X__onlI=w1920-h927-iv2?auditContext=prefetch"},{"name":"Albedo","url":"https://lh3.google.com/u/0/d/1Ms2LAC_FdgOYPojbjkYIdpOHWND4FmSM=w1920-h927-iv2?auditContext=prefetch"},{"name":"Alhaitham","url":"https://lh3.google.com/u/0/d/1EyiK5kVRVeAyS-37wo_qqwsQXgMD954Q=w1920-h927-iv2?auditContext=prefetch"},{"name":"Aloy","url":"https://i.redd.it/fdu1ddahkvt71.jpg"},{"name":"Alyosha","url":"https://lh3.google.com/u/0/d/1wiUwK49GXC0_RXuA6XzEIjZaKobFLK_m=w1920-h927-iv2?auditContext=prefetch"},{"name":"Amber","url":"https://lh3.google.com/u/0/d/1XTxNNmjI7JQ4pRim4n1xThJsyxt6pIcn=w1920-h927-iv2?auditContext=prefetch"},{"name":"Arataki Itto","url":"https://lh3.google.com/u/0/d/1z8qfEtExgPdhj91XfJBT2UDTbNxPKLZb=w1920-h927-iv2?auditContext=prefetch"},{"name":"Arlecchino","url":"https://www.wallpaperalchemy.com/storage/wallpapers/3752/arlecchino-genshin-impact-dark-flame-wallpaper.jpg"},{"name":"Baizhu","url":"https://lh3.google.com/u/0/d/1CLs81yt-56mvGHoXf8DIMSnL9-q6IQAD=w1920-h927-iv2?auditContext=prefetch"},{"name":"Barbara","url":"https://lh3.google.com/u/0/d/1q0BDt8u_V3mUdlx-6JzY131MVzaPf3SY=w1920-h927-iv2?auditContext=forDisplay"},{"name":"Beidou","url":"https://lh3.google.com/u/0/d/1GCvv5KQtlv-24InA60r_ekJy2X-bIIZV=w1920-h927-iv2?auditContext=prefetch"},{"name":"Bennett","url":"https://upload-os-bbs.hoyolab.com/upload/2023/03/25/129905032/53d1e61180439fc4560fa051a36373d3_2983537099642360859.png"},{"name":"Candace","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTXAsddXW_ipbp-rcbzLSszKmvxhJdtwigd2WtJFJUgzgugHJIWB1uNgsKw&s=10"},{"name":"Charlotte","url":"https://lh3.google.com/u/0/d/1NtaKqcz0mDoS0Zr_XeFxk2vW75iGwNNy=w1920-h927-iv2?auditContext=prefetch"},{"name":"Chasca","url":"https://lh3.google.com/u/0/d/1Pcdd47PX6z3qMPdkJdM2DQgihIAkFKnc=w1920-h927-iv2?auditContext=prefetch"},{"name":"Chevreuse","url":"https://lh3.google.com/u/0/d/1wynMGchW7z_e-3aLHL65q0KsWRBBmerm=w1920-h927-iv2?auditContext=prefetch"},{"name":"Chiori","url":"https://lh3.google.com/u/0/d/1MAIR4lbID3kX3SPkc1mBnq5UZX2ziiLj=w1920-h927-iv2?auditContext=prefetch"},{"name":"Chongyun","url":"https://lh3.google.com/u/0/d/10hxO__pW4vHkxi-I6R727Ok2dm1lfLet=w1920-h927-iv2?auditContext=prefetch"},{"name":"Citlali","url":"https://cdn-media.sforum.vn/storage/app/media/bookgrinder/huong-dan-build-citlali-1.jpg"},{"name":"Clorinde","url":"https://lh3.google.com/u/0/d/1mnoizD8wq9vPw6bRvSS6OeFigc3rg7aE=w1920-h927-iv2?auditContext=prefetch"},{"name":"Collei","url":"https://lh3.google.com/u/0/d/13ammO_C5K_mmp5REhTDxAs_1IFMcl6Fc=w1920-h927-iv2?auditContext=prefetch"},{"name":"Columbina","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQSN0RFs0XAqLiqNZYV6EibjahkyJwa9_C36MW08xLEwW2ldEd-ltnSCUQz&s=10"},{"name":"Cyno","url":"https://lh3.google.com/u/0/d/15mGe6Amd6_8xudDcEmQFazzGutzh10n5=w1920-h927-iv2?auditContext=prefetch"},{"name":"Dahlia","url":"https://lh3.google.com/u/0/d/1RlOH9_4EJeHGDYERXfWcTm5Jh6tx9l04=w1920-h927-iv2?auditContext=prefetch"},{"name":"Dehya","url":"https://lh3.google.com/u/0/d/1CaHNZr3tQIyixzQuz0zevpKx2jmLVWgB=w1920-h927-iv2?auditContext=prefetch"},{"name":"Diluc","url":"https://lh3.google.com/u/0/d/18NFp-eyGqfg_tE5M7t3JTZkSLtTs1Jeg=w1920-h927-iv2?auditContext=prefetch"},{"name":"Diona","url":"https://lh3.google.com/u/0/d/1CHPwID6ohBhzrQjDiexVjiX-G4r-y4l-=w1920-h927-iv2?auditContext=prefetch"},{"name":"Dori","url":"https://lh3.google.com/u/0/d/1UQFOS39aXaws_h6ul4On_i3QYn9iwnWW=w1920-h927-iv2?auditContext=prefetch"},{"name":"Durin","url":"https://lh3.google.com/u/0/d/17YYCy_FxHPTCX5Lgc8RJZLOJ_qzVS2_P=w1920-h927-iv2?auditContext=prefetch"},{"name":"Emilie","url":"https://i.pinimg.com/236x/02/e3/6c/02e36c2eb4d0be79138e3ce5b7ae38e2.jpg"},{"name":"Escoffier","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTqSOQe_LqAZ-2jdoqHAgbKRJbifArUuC6nHxzampcNcQ&s=10"},{"name":"Eula","url":"https://lh3.google.com/u/0/d/10s3hC3yBB7BpvC5prEthZOXoqKzwWbQ6=w1920-h927-iv2?auditContext=prefetch"},{"name":"Faruzan","url":"https://lh3.google.com/u/0/d/1K3ofwaQxb35dsbGHQxjB-46YAHoKi1xE=w1920-h927-iv2?auditContext=prefetch"},{"name":"Fischl","url":"https://preview.redd.it/why-do-you-main-love-fischl-outside-of-meta-v0-vbjarco1ge5d1.jpeg?auto=webp&s=b22fa59a819d904aec372ad6c745e66dd04af99f"},{"name":"Flins","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTw35nyFm-wdwrXv2Dzbwh1bS3k4yGVb0p9l689S2fZrg&s=10"},{"name":"Freminet","url":"https://lh3.google.com/u/0/d/1m9WbShoR6Ob7E6p4Jood2N6GFVvNEEWM=w1920-h927-iv2?auditContext=prefetch"},{"name":"Furina","url":"https://lh3.google.com/u/0/d/1dq4O1tteDyhPhYW6BFkWGI0FCNYxI-Yj=w1920-h927-iv2?auditContext=prefetch"},{"name":"Gaming","url":"https://lh3.google.com/u/0/d/1HTPZV47FGacQanMBSMDLhNm7OfVa15a9=w1920-h927-iv2?auditContext=prefetch"},{"name":"Ganyu","url":"https://lh3.google.com/u/0/d/1osmQSYVp-ZscRP3BSq7qcaQ2JDT-YGg0=w1920-h927-iv1?auditContext=prefetch"},{"name":"Gorou","url":"https://i.pinimg.com/736x/46/64/94/46649420ce8606bb133c60a4dc47b6bb.jpg"},{"name":"Hu Tao","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQMGbRkm-HS3T1bsnLHcziE2sIp-pA4tCyGiSmtxQmC7A&s=10"},{"name":"Iansan","url":"https://lh3.google.com/u/0/d/1_AbNqAoxERX-KqDf8zs4QET1tBMsmokY=w1920-h927-iv2?auditContext=prefetch"},{"name":"Ifa","url":"https://lh3.google.com/u/0/d/1PiWPmzC-MVk09StVIqKmQe1ERjSz0Ye7=w1920-h927-iv2?auditContext=prefetch"},{"name":"Illuga","url":"https://lh3.google.com/u/0/d/1bhIXN1UYnIxvtX0gYfs5r9WFCucVlhje=w1920-h927-iv2?auditContext=prefetch"},{"name":"Ineffa","url":"https://lh3.google.com/u/0/d/1DPTrSxKD1EfWXLd2gpcktNEZEs6KsG1I=w1920-h927-iv1?auditContext=prefetch"},{"name":"Jahoda","url":"https://lh3.google.com/u/0/d/1DzX2hOqT0m9RKhs00bRrMEWy84x4P2FJ=w1920-h927-iv2?auditContext=prefetch"},{"name":"Jean","url":"https://lh3.google.com/u/0/d/1TFfUyF0egxjv57ApGcQlg-CLXqsVC431=w1920-h927-iv2?auditContext=prefetch"},{"name":"Kachina","url":"https://lh3.google.com/u/0/d/1L4V3nzFxPBMEmd9b5vzeYt0WTFiis15p=w1920-h927-iv2?auditContext=prefetch"},{"name":"Kaedehara Kazuha","url":"https://i.redd.it/gkjqf81odrg81.jpg"},{"name":"Kaeya","url":"https://lh3.google.com/u/0/d/1xxDbnNg3owOfidz01T7dU14E3zv2K3no=w1920-h927-iv2?auditContext=prefetch"},{"name":"Kamisato Ayaka","url":"https://lh3.google.com/u/0/d/1HEq3rZxhEF6fAAgrdNxtBKRp7Dlo4N6w=w1920-h927-iv2?auditContext=prefetch"},{"name":"Kamisato Ayato","url":"https://lh3.google.com/u/0/d/1tSGany0qj8yVUjEC6p8kz3NkmUGNJ5Bj=w1920-h927-iv2?auditContext=prefetch"},{"name":"Kaveh","url":"https://lh3.google.com/u/0/d/1CmYbCV5SqUKEFNl9vwt4_M2PG5DGL2eN=w1920-h927-iv2?auditContext=prefetch"},{"name":"Keqing","url":"https://upload-os-bbs.hoyolab.com/upload/2023/03/26/175320580/4278991f654e5da945d760fa780a7956_2859796799533974647.jpg"},{"name":"Kinich","url":"https://lh3.google.com/u/0/d/1t9V_pH6zggFuCTerGNMPGiv1EYHO_3lY=w1920-h927-iv2?auditContext=prefetch"},{"name":"Kirara","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTqIqDdulHziahQUD1Fi83eHzddBGIt0MUQnA&s"},{"name":"Klee","url":"https://lh3.google.com/u/0/d/1X_M7pVpIszhmC-lADsSNtVd5XfA3lRG7=w1920-h927-iv2?auditContext=prefetch"},{"name":"Kujou Sara","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTsMuTWPgmFIZLoWi0wCu4rKsTafkighjuGCq9FxoDdYg&s=10"},{"name":"Kuki Shinobu","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRAPK48XjwLdno1gMCO7StDdE8FqIeQ-1bKs4DotgZulw&s=10"},{"name":"Lan Yan","url":"https://lh3.google.com/u/0/d/1OviBNboaqIwwOaXjbx8dq32wTXEVFI0q=w1920-h927-iv2?auditContext=prefetch"},{"name":"Lauma","url":"https://lh3.google.com/u/0/d/1B3TOk3DizHRD7ZjE5pKehyfjDJs9jCnd=w1920-h927-iv2?auditContext=prefetch"},{"name":"Layla","url":"https://i.pinimg.com/736x/81/1e/28/811e2845c5d965d6d053e1b486b2e123.jpg"},{"name":"Linnea","url":"https://lh3.google.com/u/0/d/19rfAWbiI8owuCHCvlZGDJM6JtcDd89SS=w1920-h927-iv2?auditContext=prefetch"},{"name":"Lisa","url":"https://lh3.google.com/u/0/d/1adQMg3kMtFXi4Vc6ACkSE-5eEi1u3K_z=w1920-h927-iv2?auditContext=prefetch"},{"name":"Lohen","url":"https://lh3.google.com/u/0/d/1Wm41QL6O8JivbA19SgKO-DUHq27sOP2d=w1920-h927-iv1?auditContext=prefetch"},{"name":"Lynette","url":"https://lh3.google.com/u/0/d/12vUW-1KmgX5xKPpyAhV6TeUUsjrwRf62=w1920-h927-iv2?auditContext=prefetch"},{"name":"Lyney","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSKlDVA9CsCi6JrbgsATN7tMecj62vX55R9TJA20XVLmQ&s=10"},{"name":"Manekin","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQT2rUwlcLh8QDfpmPMD8R6on-9jSDg1cJM5UTh0p9BxW19LNe2_nE1ows&s=10"},{"name":"Mavuika","url":"https://upload-os-bbs.hoyolab.com/upload/2024/10/28/417036116/097e093e3d47ed14de5541fc9f76f677_6575823425656404754.jpg?x-oss-process=image%2Fresize%2Cs_1000%2Fauto-orient%2C0%2Finterlace%2C1%2Fformat%2Cwebp%2Fquality%2Cq_70"},{"name":"Mika","url":"https://lh3.google.com/u/0/d/15HjP9IsglBz56V6ROrt2H2imfln2vMK6=w1920-h927-iv2?auditContext=prefetch"},{"name":"Mitya","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT7tKak31qcOO2d3fp_4DKMQ2y2zTx3zKO4wdExB2Fh2w&s=10"},{"name":"Mona","url":"https://lh3.google.com/u/0/d/1F4WIQdCJIvchjQjsVdwBLjIDZccSdxhU=w1920-h927-iv2?auditContext=prefetch"},{"name":"Mualani","url":"https://lh3.google.com/u/0/d/1qiKB0g9D3-j-3QekGr5Llob4a5FfQF2f=w1920-h927-iv2?auditContext=prefetch"},{"name":"Nahida","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRblJ2rYk9AULyM_XHv0c1QykRGOUYX8doaSQ&s"},{"name":"Navia","url":"https://lh3.google.com/u/0/d/12LoorIA6-wjhcVFuF2jnHIlHBVITAGHD=w1920-h927-iv2?auditContext=prefetch"},{"name":"Nefer","url":"https://lh3.google.com/u/0/d/1N0B0lHnQFJgnNxBISRrjroi1IjETdDhT=w1920-h927-iv2?auditContext=prefetch"},{"name":"Neuvillette","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSEPHyk6gzC81iNTmUuNCRgi3k62AYkOJFLsQoA7xEMlGNHDfImIEo6ReM9&s=10"},{"name":"Nicole","url":"https://lh3.google.com/u/0/d/1YtaV1AhVfzTo0_MYo6VXHFObHgc1F1Hm=w1920-h927-iv2?auditContext=prefetch"},{"name":"Nilou","url":"https://lh3.google.com/u/0/d/1ABfHTkRe1K9QxcQQIkOI5iv0pMHwjMtM=w1920-h927-iv2?auditContext=prefetch"},{"name":"Ningguang","url":"https://lh3.google.com/u/0/d/1a0HMDofy1z_g3qQu6DUSxbhHSm7wXCOz=w1920-h927-iv2?auditContext=prefetch"},{"name":"Noelle","url":"https://lh3.google.com/u/0/d/1ImeJgP7w4HRYMxbfEBelrrkATXF-dJ6f=w1920-h927-iv2?auditContext=prefetch"},{"name":"Odette","url":"https://i.pinimg.com/236x/13/25/5f/13255ffd44bce1b83f3d35fb344e6764.jpg"},{"name":"Ororon","url":"https://lh3.google.com/u/0/d/1CNimMHkRvw0b6BZwWk9lDh9o1ZLq6UBb=w1920-h927-iv2?auditContext=prefetch"},{"name":"Prune","url":"https://lh3.google.com/u/0/d/1rYVuxz9QB7BIzGq3dxxSmK649t5QD3Pg=w1920-h927-iv2?auditContext=prefetch"},{"name":"Qiqi","url":"https://lh3.google.com/u/0/d/17nycPJuPGKoRrdcs5OQyn6uzRgp9Ng90=w1920-h927-iv2?auditContext=prefetch"},{"name":"Raiden Shogun","url":"https://lh3.google.com/u/0/d/1-UzQLSGlue45aFq5VA8J18cspTFCtnjN=w1920-h927-iv2?auditContext=prefetch"},{"name":"Razor","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSDy2I7Lcq84O6TzdjI3Gyk_8DfmhKarzOXgHszCbQ4i93ojz0ePT_4jJY&s=10"},{"name":"Rosaria","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQU1yArOriY6C3YMF7NBgmJdWK0pS8yjufh2RUcD-Jl1f9onExqWtM7fyA&s=10"},{"name":"Sandrone","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSOSTUMoNCETovRHoJ3qKiZvmrk0BrrjA6Cx1xq7KOS3B-QiJwQl3aV6O0&s=10"},{"name":"Sangonomiya Kokomi","url":"https://cdn2.fptshop.com.vn/unsafe/Uploads/images/tin-tuc/165403/Originals/hinh-anh-sangonomiya-kokomi%20(1).jpg"},{"name":"Sayu","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxSUAvO6KjQNCMCUIBaSbJTgnvQ-zxCZ490xS6bcalSw&s=10"},{"name":"Sethos","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRjp5r8en7PNX1GCP96vumGzb0uV6E164mwfMSCs5zhUA&s=10"},{"name":"Shenhe","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTq5EiSOC73nP61pCPDJ2d_CJ0DqnCxVBeMPeYKr2KVFQ&s=10"},{"name":"Shikanoin Heizou","url":"https://lh3.google.com/u/0/d/1mEDud-i-5JZyi9Ili941mqCv5BPQihW4=w1920-h927-iv2?auditContext=prefetch"},{"name":"Sigewinne","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYK-mTddBJFEo5JHo0B9LTf4sFo_pnMTGedI5H0ICcBc9xAg2pvHBz_eK4&s=10"},{"name":"Skirk","url":"https://upload-os-bbs.hoyolab.com/upload/2025/06/23/354290382/4bc37e5b64f3bc117dc4c9781c4e260b_6499707882575441908.jpg?x-oss-process=image%2Fresize%2Cs_1000%2Fauto-orient%2C0%2Finterlace%2C1%2Fformat%2Cwebp%2Fquality%2Cq_70"},{"name":"Sucrose","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSPbqV6ABrbFL117eCiWVjxltVslosAiWqUsn_ZfL8E-A&s=10"},{"name":"Tartaglia","url":"https://lh3.google.com/u/0/d/16HLxJ6vZPsh6Gh9I7I-a-ran6AiO7KkR=w1920-h927-iv2?auditContext=prefetch"},{"name":"Thoma","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQVDx-3fgwTiMIdT0-jz2w1AoHk8BjLGNwlTJ_wVc1RJw&s=10"},{"name":"Tighnari","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSPxPJXoXTbJHVJAiDUrcahx2ccOCMM4KkxQ8evq0njEOvVcdA72IoC3fHo&s=10"},{"name":"Traveler","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQs69ZRc7IizDopIFsoR2P0h7AxsA3BeIKMq8yafWZ8kzvILHCTLcBV-2DD&s=10"},{"name":"Valeriy","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTfTmCdZ2VbVxGuZxiuYaM19dulpJPZJ1f4pjJiwZ0uGg&s=10"},{"name":"Varesa","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSzZdIDKO4qW17_t7HwYbPHU1nOdfFz81jaly44BeE5Bg&s=10"},{"name":"Varka","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSWGk8UaAe8LS0EibLbWro-HmBnsNcmxadCXaJXxYoG_A&s=10"},{"name":"Venti","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSnXoF7g17He56p8ARqauGeTwVph5IFiNT8EdnFvTk0qQ&s=10"},{"name":"Vesna","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSpnqXDGWqoYE75mWkeU-yjWuUPoiVChAYRUGzRXzV1lA&s=10"},{"name":"Vodyanitsa","url":"https://lh3.google.com/u/0/d/1Hup1DoGl-YukQYfWL4kOi90auTxErvfU=w1920-h927-iv2?auditContext=prefetch"},{"name":"Wanderer","url":"https://lh3.google.com/u/0/d/1OQnzTycT-X13cnQVGoI7krROJZGTE5uj=w1920-h927-iv1?auditContext=prefetch"},{"name":"Wriothesley","url":"https://lh3.google.com/u/0/d/1tRR1A9tYJ0xRd-AlOMS6X0hEm709NSTb=w1920-h927-iv2?auditContext=prefetch"},{"name":"Xiangling","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSjfqWlfz9l5uf3iACAGKDtObJ_VZSyZBpu9Ye9hbXByA&s=10"},{"name":"Xianyun","url":"https://lh3.google.com/u/0/d/1C-h5bBc7nz08lkb1GNH5cEVJywWibuC7=w1920-h927-iv2?auditContext=prefetch"},{"name":"Xiao","url":"https://lh3.google.com/u/0/d/1GCqMZuNSHqv9VFXkZhyAERMkT4kStF6M=w1920-h927-iv1?auditContext=prefetch"},{"name":"Xilonen","url":"https://lh3.google.com/u/0/d/1eIry_SWfpAUKp6PzNXqZeCpsWWG7MPWj=w1920-h927-iv1?auditContext=prefetch"},{"name":"Xingqiu","url":"https://lh3.google.com/u/0/d/1ir5x3hPygndCJZ5kt9WmYKpkqEvfNSNR=w1920-h927-iv2?auditContext=prefetch"},{"name":"Xinyan","url":"https://lh3.google.com/u/0/d/1pgIl1cFN_1mULbLJdkDYkpSxftrTlfg1=w1920-h927-iv2?auditContext=prefetch"},{"name":"Yae Miko","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSLPSYySuq7n-dqgus-mfxnKZImivNk3ZkiZgI4Qs2B5wXylcKwXhYevv8h&s=10"},{"name":"Yanfei","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTuwP5Ic5LS1rPoxoZ_YLIEK9GMgsseqU5EokiHWhyCZW8AB4sY5thzrwlD&s=10"},{"name":"Yaoyao","url":"https://i.redd.it/lcym0vio0nmc1.jpg"},{"name":"Yelan","url":"https://lh3.google.com/u/0/d/10OVxRru9SdulWe6jhM-PYGUxnPSgEwwj=w1920-h927-iv2?auditContext=prefetch"},{"name":"Yoimiya","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ7RhLI4yw3O1NrzruwE3QRa8y-VtQl5knLXA&s"},{"name":"Yumemizuki Mizuki","url":"https://i.pinimg.com/736x/72/39/a2/7239a2fd00cadd8ffb55da7febd518f1.jpg"},{"name":"Yun Jin","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRpDweTl3yvN-hDloNIFrUC_MNjyYZbeiW_1D1k-LAl4a8Ix74v-usZuqQ&s=10"},{"name":"Zhongli","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQcCWzhTrRd1eK3HQThbXM5-A1au-Gl4cWp6TuoCbEDMA&s=10"},{"name":"Zibai","url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSV1NGXYZ989nyidELZ7j3TV0qyZUx8aBRFnOwiq-73eg&s=10"}
]

OUT_IMG = "public/assets/characters-sprite.webp"
OUT_CSS = "public/assets/characters.css"
OUT_MAP = "public/assets/sprite-map.json"
ICON_SIZE = 128

os.makedirs(os.path.dirname(OUT_IMG), exist_ok=True)

seen = set()
unique_chars = []
for item in CHARACTERS:
    url = (item.get("url") or "").strip()
    if url and url not in seen:
        seen.add(url)
        unique_chars.append((item.get("name") or "Unknown", url))

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})

def build_candidate_urls(raw_url):
    # Trích xuất Google Drive File ID nếu là link Drive / lh3.google.com
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", raw_url)
    if match and ("google.com" in raw_url or "googleusercontent.com" in raw_url):
        file_id = match.group(1)
        return [
            f"https://drive.google.com/thumbnail?id={file_id}&sz=w256",
            f"https://lh3.googleusercontent.com/d/{file_id}=w256",
            f"https://drive.google.com/uc?export=download&id={file_id}",
        ]
    return [raw_url]

def download_image(raw_url):
    last_err = None
    for candidate in build_candidate_urls(raw_url):
        try:
            resp = session.get(candidate, timeout=15, allow_redirects=True)
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" in content_type:
                last_err = "File chưa bật 'Bất kỳ ai có đường liên kết' trên Google Drive"
                continue
            img = Image.open(BytesIO(resp.content)).convert("RGBA")
            return img.resize((ICON_SIZE, ICON_SIZE), Image.Resampling.LANCZOS)
        except UnidentifiedImageError:
            last_err = "Dữ liệu trả về không phải ảnh (có thể do chưa mở quyền Drive)"
        except Exception as e:
            last_err = str(e)
    raise RuntimeError(last_err or "Không tải được ảnh")

downloaded = []
for i, (name, url) in enumerate(unique_chars):
    try:
        img = download_image(url)
        downloaded.append((name, url, img))
        print(f"[{i+1}/{len(unique_chars)}] OK: {name}")
    except Exception as e:
        print(f"[{i+1}/{len(unique_chars)}] LỖI - {name}: {e}")

total = len(downloaded)
if total == 0:
    raise RuntimeError("Không tải được ảnh nào, hãy kiểm tra lại quyền chia sẻ thư mục Google Drive!")

cols = math.ceil(math.sqrt(total))
rows = math.ceil(total / cols)
sprite = Image.new("RGBA", (cols * ICON_SIZE, rows * ICON_SIZE), (0, 0, 0, 0))

css_lines = [
    ".char-icon {",
    "  display: inline-block;",
    "  width: 64px;",
    "  height: 64px;",
    "  background-image: url('/assets/characters-sprite.webp');",
    f"  background-size: {cols * 100}% {rows * 100}%;",
    "  background-repeat: no-repeat;",
    "}\n"
]
sprite_map = {}

for idx, (name, url, img) in enumerate(downloaded):
    col = idx % cols
    row = idx // cols
    sprite.paste(img, (col * ICON_SIZE, row * ICON_SIZE))

    class_name = f"char-{idx}"
    pos_x = (col / (cols - 1) * 100) if cols > 1 else 0
    pos_y = (row / (rows - 1) * 100) if rows > 1 else 0

    css_lines.append(f"/* {name} */")
    css_lines.append(f".{class_name} {{ background-position: {pos_x:.4f}% {pos_y:.4f}%; }}")
    sprite_map[url] = class_name

sprite.save(OUT_IMG, "WEBP", quality=82, method=6)
with open(OUT_CSS, "w", encoding="utf-8") as f:
    f.write("\n".join(css_lines))
with open(OUT_MAP, "w", encoding="utf-8") as f:
    json.dump(sprite_map, f, indent=2, ensure_ascii=False)

print(f"\nHoàn tất! Đã đóng gói {total}/{len(unique_chars)} icon vào {OUT_IMG}")