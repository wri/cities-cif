import coiled
from distributed import Client

from cities_indicators.core import get_city_indicators, get_indicators, Indicator
from cities_indicators.city import get_city_admin, API_URI
from cities_indicators.layers.esa_world_cover import EsaWorldCover, EsaWorldCoverClass
from cities_indicators.layers.land_surface_temperature import LandSurfaceTemperature

import pandas as pd
import geopandas as gpd
import pytest


def get_baseline(indicator_name):
    df = pd.read_csv("fixtures/jakarta_baseline.csv")
    return df[["geo_id", indicator_name]]


def test_tree_cover_in_built_up_areas():
    jakarta = get_city_admin("IDN-Jakarta")[1:]
    indicators = get_city_indicators(cities=jakarta, indicators=[Indicator.BUILT_LAND_WITH_TREE_COVER])[0]
    baseline_indicators = get_baseline("HEA_4_percentBuiltupWithoutTreeCover")

    for actual, baseline in zip(indicators["HEA_4_percentBuiltupWithoutTreeCover"],
                                ACTUAL_BUILT_TTC_VALUES):
        # TODO some are a little off due to differences with GEE counting
        assert pytest.approx(actual, abs=0.02) == baseline


def test_surface_reflectivity():
    jakarta = get_city_admin("IDN-Jakarta")[1:]
    indicators = get_city_indicators(cities=jakarta, indicators=[Indicator.SURFACE_REFLECTIVTY])[0]

    for actual, baseline in zip(indicators["HEA_3_percentBuiltwLowAlbedo"], ACTUAL_ALBEDO_VALUES):
        assert pytest.approx(actual, abs=0.015) == baseline


def test_high_lst():
    jakarta = get_city_admin("IDN-Jakarta")[1:]
    indicators = get_city_indicators(cities=jakarta, indicators=[Indicator.BUILT_LAND_WITH_HIGH_LST])[0]
    baseline_indicators = get_baseline("HEA_2_percentBuiltupwHighLST-2013to2022meanofmonthwhottestday")

    for actual, baseline in zip(indicators["HEA_2_percentBuiltupwHighLST-2013to2022meanofmonthwhottestday"], baseline_indicators["HEA_2_percentBuiltupwHighLST-2013to2022meanofmonthwhottestday"]):
        assert pytest.approx(actual, abs=1) == baseline


def test_tree_cover():
    jakarta = get_city_admin("IDN-Jakarta")[1:]
    indicators = get_city_indicators(cities=jakarta, indicators=[Indicator.TREE_COVER])[0]
    baseline_indicators = get_baseline("LND_2_percentTreeCover")

    for actual, baseline in zip(indicators["LND_2_percentTreeCover"], baseline_indicators["LND_2_percentTreeCover"]):
        assert pytest.approx(actual, abs=0.01) == baseline


def test_gdf():
    url = f"{API_URI}/IDN-Jakarta/ADM4union/geojson"
    gdf = gpd.read_file(url)
    gdf = gdf.to_crs("3857")[["id", "geometry"]]

    indicators = get_indicators(gdf, indicators=[Indicator.TREE_COVER, Indicator.SURFACE_REFLECTIVTY])
    assert len(indicators) == 2


def test_lst():
    url = f"{API_URI}/IDN-Jakarta/ADM4/geojson"
    jakarta = gpd.read_file(url)

    #lst = g.land_surface_temperature(start_date="2022-12-24", end_date="2023-01-01", output_path="")

    lst = LandSurfaceTemperature(start_date="2022-12-24", end_date="2023-01-01")
    built_up = EsaWorldCover(land_cover_class=EsaWorldCoverClass.BUILT_UP)
    lst_by_admin_area = lst.mask(built_up).groupby(jakarta).mean()

    # ttc = TropicalTreeCover(min_cover=1)
    #
    # built_up.count()
    # ttc.mask(built_up).groupby(jakarta).count()

    print(lst_by_admin_area)


ACTUAL_ALBEDO_VALUES = [
    0.9221448467966574,
    0.8811335403726708,
    0.9714214088744046,
    0.9280688985929161,
    0.9277950310559007,
    0.9425612972550552,
    0.9417005109393424,
    0.9490838206627681,
    0.9685985247629083,
    0.9850713012477719,
    0.9295091508762853,
    0.9477234401349073,
    0.9681486396814863,
    0.906364711006035,
    0.8972642607683353,
    0.9435139573070608,
    0.9615384615384616,
    0.9549437503533269,
    0.9346728882963528,
    0.9349923819197562,
    0.9482735274204469,
    0.9782359081419624,
    0.9179784589892295,
    0.9393855776306107,
    0.9354248270307867,
    0.9806906416019616,
    0.9764681237343761,
    0.8819728623734654,
    0.9528485271395105,
    0.9452742123687281,
    0.9102880658436214,
    0.9188737106216894,
    0.9334604157979389,
    0.8822008862629247,
    0.9401650618982118,
    0.9787512734681997,
    0.9178218843521034,
    0.9524219797051503,
    0.9049810192108593,
    0.9627738054704347,
    0.8832479662548961,
    0.9361242628125259,
    0.9744619338258914,
    0.8787192144803215,
    0.919396183423526,
    0.9636464978014492,
    0.887800599371391,
    0.9460482725982016,
    0.9194106220685081,
    0.8654857560262965,
    0.8630653266331658,
    0.9066769176178366,
    0.9076275542989333,
    0.9735880398671096,
    0.9550102249488752,
    0.8673017366419695,
    0.9573341326938449,
    0.9731119732924298,
    0.8167465587756717,
    0.9001434205808534,
    0.9307628903745764,
    0.8941657773034507,
    0.9589974521538188,
    0.9361516289632282,
    0.9365789556021401,
    0.9711428571428572,
    0.9548002803083392,
    0.8904206267055613,
    0.9584389616881493,
    0.9605202754399388,
    0.9521013337807231,
    0.9693877551020408,
    0.9439985867151222,
    0.9557296411003826,
    0.950355526826115,
    0.9547482472912683,
    0.9688846536294332,
    0.9331397107763054,
    0.9087621696801113,
    0.9844889454798009,
    0.9623217922606925,
    0.9418589660951399,
    0.9713330988392543,
    0.9653341470857492,
    0.9793103448275862,
    0.8793335294364836,
    0.9638931492842536,
    0.9321915414190842,
    0.9452127098068194,
    0.9216007612603088,
    0.902793321097632,
    0.8862982744453575,
    0.9438528557599225,
    0.9640787949015064,
    0.9779289744440757,
    0.918114667604643,
    0.9577861163227017,
    0.9278051609162076,
    0.8658381134480561,
    0.8836211326960633,
    0.939728779507785,
    0.9411764705882353,
    0.9706062046025389,
    0.7812717805748022,
    0.9595502536679007,
    0.9644682115270351,
    0.9241832751181426,
    0.938206401183057,
    0.943743063263041,
    0.8613224637681159,
    0.9013484289530594,
    0.9083885209713024,
    0.8818044813937698,
    0.9427552552552553,
    0.9549156242129124,
    0.9602952913008779,
    0.9529835008063515,
    0.9398334676336287,
    0.9670325031658927,
    0.9850662384584504,
    0.9659658617818485,
    0.9513471253307674,
    0.943905635648755,
    0.9684651841049945,
    0.9398489480309297,
    0.957256258904946,
    0.9712574850299401,
    0.9364130799704559,
    0.9625,
    0.944553855476443,
    0.9466584917228694,
    0.9460338101430429,
    0.9670223752151463,
    0.9646912873365779,
    0.8719392752203722,
    0.8896672504378283,
    0.9386834986474302,
    0.9286277602523659,
    0.8778747026169706,
    0.9460249933528317,
    0.9260260897231944,
    0.8823114869626497,
    0.8933429513602638,
    0.7631310616300301,
    0.9443151298119964,
    0.9633802816901409,
    0.9598281960586155,
    0.9245351804593511,
    0.9551971326164874,
    0.9585042219541616,
    0.9534465020576132,
    0.9446457990115321,
    0.9764375159723997,
    0.9692968601933161,
    0.910793768545994,
    0.9342993251290195,
    0.9199018771331058,
    0.9357839595375722,
    0.9572143233280674,
    0.9221244219006415,
    0.9183893971043723,
    0.8707730986800755,
    0.8418447422431486,
    0.9718261212809,
    0.9547410084322836,
    0.9663290779566074,
    0.9692001447701774,
    0.953721962040917,
    0.9690086501960297,
    0.9643896593049135,
    0.9612828918224506,
    0.9495212038303693,
    0.9746497077225862,
    0.967991898912517,
    0.971785175979057,
    0.9548661707186133,
    0.9345026034530008,
    0.9336885731201895,
    0.9060891176992721,
    0.9338751385297377,
    0.9035213511790949,
    0.9493006673370509,
    0.915623869801085,
    0.9520316921335598,
    0.9583065242568524,
    0.9431263480531275,
    0.9821700507614213,
    0.9617943498336726,
    0.9697761343997428,
    0.8968714298268741,
    0.9661454792658056,
    0.9571206398578094,
    0.9049892968878643,
    0.9291930963268918,
    0.9693474962063733,
    0.9657443030482391,
    0.9591272396681693,
    0.977996395313908,
    0.9726965206185567,
    0.9688793246151299,
    0.9740640634884122,
    0.9665599430807542,
    0.9413120800948491,
    0.9439339608546242,
    0.9441545181235464,
    0.959487563430663,
    0.9187221447283367,
    0.9006178572870815,
    0.9537928106425134,
    0.9682744903033317,
    0.9472177109154628,
    0.9437456807187284,
    0.9590914227596339,
    0.9433594836699494,
    0.969445770582874,
    0.9532314017730952,
    0.9704647066793117,
    0.9460418885339014,
    0.9538525355179923,
    0.9786585365853658,
    0.8267467594056276,
    0.8848757181047722,
    0.7802642796248934,
    0.7445881731784583,
    0.8983202505389026,
    0.8640632110205602,
    0.9143398827990348,
    0.9068341277917626,
    0.8759220598469033,
    0.9226042230644288,
    0.8990960598590026,
    0.9016256684491979,
    0.7691271762042314,
    0.8365502032186924,
    0.8788437780297518,
    0.9742064660502915,
    0.9369780421232737,
    0.8130068115471943,
    0.8952279957582184,
    0.8910436928436638,
    0.8602663985926112,
    0.8998548621190131,
    0.9659239842726082,
    0.964566102691129,
    0.9537676056338028,
    0.9738912732474965,
    0.9446661475569399,
    0.9105101756342348,
    0.9455002794857462,
    0.867653545043555,
    0.869419737399407,
    0.9335732209649165,
    0.8835970861592565,
    0.9470284637018265,
    0.9494234555170151,
    0.9449816062766546,
    0.9533268875802057,
    0.9643633202955237,
    0.9576385439579933,
    0.9118321283724211,
    0.9644056706652127,
    0.9559794214715589]

ACTUAL_BUILT_TTC_VALUES = [0.7875765949777724,
                           0.7640524625267666,
                           0.8969172525689562,
                           0.926324589821298,
                           0.9566570348966437,
                           0.8320658795848914,
                           0.901259559154296,
                           0.7809173083361232,
                           0.9186829179552483,
                           0.7485593545908567,
                           0.8056403708432799,
                           0.8481407258962369,
                           0.980386583285958,
                           0.9368494101318529,
                           0.9880254459274043,
                           0.7844656524614948,
                           0.8433042367468597,
                           0.855808977289306,
                           0.988332922520746,
                           0.8585039973715913,
                           0.8992364645997224,
                           0.8144875532630634,
                           0.9246284501061571,
                           0.901722231000158,
                           0.8612253870552398,
                           0.7276252588904067,
                           0.732020650738384,
                           0.9607480096278467,
                           0.7902014339364971,
                           0.7521230491745785,
                           0.9666745450248169,
                           0.9781774580335731,
                           0.797875057465393,
                           0.944110196326789,
                           0.9967570754716981,
                           0.8126175253854833,
                           0.8768456968056945,
                           0.905318623415116,
                           0.7546236771832657,
                           0.7713477115253244,
                           0.6887109274089382,
                           0.8774014515440444,
                           0.9089024053082665,
                           0.8439502973366962,
                           0.8086007493077049,
                           0.8034994697773065,
                           0.9407737721391785,
                           0.7632214287529544,
                           0.80562213104765,
                           0.8331085531474454,
                           0.9527665317139001,
                           0.8653055005332927,
                           0.843277206713148,
                           0.8108856088560885,
                           0.8597795604252266,
                           0.8741103800187995,
                           0.8764518626860536,
                           0.8345975232198142,
                           0.8968582837338959,
                           0.9635633781071484,
                           0.9409259405315876,
                           0.9097600245342329,
                           0.7392746008264042,
                           0.82634416654186,
                           0.8233919071417056,
                           0.8080064500297963,
                           0.9695140356172653,
                           0.8927719127937548,
                           0.8589349403517402,
                           0.8254427494301245,
                           0.9070723091341648,
                           0.8208583868961228,
                           0.8332500271650549,
                           0.9776942944353134,
                           0.9031738985684163,
                           0.8965643052599575,
                           0.8407309774864634,
                           0.9005094084624181,
                           0.9922489864059146,
                           0.8604581673306773,
                           0.7117893571598007,
                           0.8625513489508161,
                           0.8078262185891614,
                           0.6686532831451275,
                           0.9346963686298444,
                           0.8405072882089768,
                           0.8628107336881963,
                           0.9204170417041704,
                           0.8531191700414069,
                           0.8623782208868251,
                           0.8172065831870189,
                           0.8007462023629741,
                           0.9030915576694412,
                           0.9170994806232521,
                           0.924567276871572,
                           0.937193683064077,
                           0.8639346291940077,
                           0.9280539595303522,
                           0.9262693035631018,
                           0.8731475992886781,
                           0.9279775402224382,
                           0.9063479623824451,
                           0.8715178414997372,
                           0.9383689745218434,
                           0.8189970501474926,
                           0.8354475703324808,
                           0.9124165238461084,
                           0.8982544994121371,
                           0.892499403768185,
                           0.8509156884333277,
                           0.9562599222641922,
                           0.9133193995819875,
                           0.8108867078913031,
                           0.8493985565356856,
                           0.8748465371560628,
                           0.7499357271402862,
                           0.8390996693098176,
                           0.8848124048179427,
                           0.8920774456028189,
                           0.9153739612188365,
                           0.8310406431442608,
                           0.817079463364293,
                           0.9273177317731773,
                           0.9658307210031348,
                           0.8666820880561339,
                           0.9318340917045852,
                           0.8639667705088265,
                           0.8927194244604316,
                           0.9217059197963081,
                           0.9277879341864717,
                           0.8660721033935455,
                           0.9205548549810845,
                           0.7200944231336677,
                           0.982392924412415,
                           0.688544502617801,
                           0.9117991631799163,
                           0.9813664596273292,
                           0.965330627431084,
                           0.9381537062301046,
                           0.9915195966078386,
                           0.9775956284153006,
                           0.9739866908650938,
                           0.8859197443181819,
                           0.9034266644961745,
                           0.8240313653136532,
                           0.7179633053619685,
                           0.7988911838243287,
                           0.8216799624589395,
                           0.7987647967061245,
                           0.7890371189603926,
                           0.858845045444469,
                           0.779807543868677,
                           0.8358990147783252,
                           0.8357127288578902,
                           0.9558329332693231,
                           0.9557597413646418,
                           0.9244036697247706,
                           0.8223464554701452,
                           0.7003389830508475,
                           0.9254498714652957,
                           0.7501081916537867,
                           0.9244814174589455,
                           0.9053969901401142,
                           0.8896528308293015,
                           0.8934687523167025,
                           0.8298540260555642,
                           0.8371984725714818,
                           0.7490724053853492,
                           0.7679295624332978,
                           0.7732447354277617,
                           0.9355723098012337,
                           0.950187969924812,
                           0.8041510100118529,
                           0.824827430123345,
                           0.8315652590513997,
                           0.8358778625954199,
                           0.9204225352112676,
                           0.9421178072863466,
                           0.8167251640470014,
                           0.927856348323534,
                           0.8621968812255272,
                           0.7973650698822456,
                           0.7683051954108758,
                           0.817564147490558,
                           0.7986912727005367,
                           0.9139029211508896,
                           0.8057716482355299,
                           0.833614450114226,
                           0.8400193999861428,
                           0.8670900430936721,
                           0.8506432748538012,
                           0.9370696250956388,
                           0.9562198923207708,
                           0.9392553056296861,
                           0.8327557559933539,
                           0.7934478371501272,
                           0.8694265442947341,
                           0.8279201911280429,
                           0.7986159169550173,
                           0.7582644628099173,
                           0.7624074987666503,
                           0.8084140744518102,
                           0.8228027426758089,
                           0.6717638007309098,
                           0.8416335874144607,
                           0.8285018967862,
                           0.8725367121128076,
                           0.8556363636363636,
                           0.9408834072543897,
                           0.7709904043865661,
                           0.8035156106350899,
                           0.8632926466210181,
                           0.8755969203781307,
                           0.8148395085246214,
                           0.7970782245742183,
                           0.7903404067197171,
                           0.8779290597791153,
                           0.7432422200348301,
                           0.6755571466929204,
                           0.7029901356350186,
                           0.9263231648162121,
                           0.9370348609479044,
                           0.8530987547060527,
                           0.9356205474315711,
                           0.9415186236378289,
                           0.9007299270072993,
                           0.8391618758956957,
                           0.8817551217938377,
                           0.8992775853537852,
                           0.9105209349876853,
                           0.848162079624595,
                           0.8454064418591788,
                           0.7643381490295981,
                           0.7570162135117809,
                           0.7258462879558332,
                           0.7832572298325723,
                           0.8546270960499545,
                           0.8917886696371737,
                           0.8157318968509046,
                           0.8742660357257885,
                           0.880904739485248,
                           0.8424717681677425,
                           0.7773495871018482,
                           0.8817785464634453,
                           0.7787434365381134,
                           0.8565539621979564,
                           0.8723581989808704,
                           0.8299172959367134,
                           0.9087740384615385,
                           0.8686112361680449,
                           0.842476845533781,
                           0.8628619063109955,
                           0.8695295109247693,
                           0.7929940515532056,
                           0.7496370382319729,
                           0.7727794739643148,
                           0.81198745323306,
                           0.8783586398994531,
                           0.8611382510991695,
                           0.9171776057895266,
                           0.8290920042162325]

                    