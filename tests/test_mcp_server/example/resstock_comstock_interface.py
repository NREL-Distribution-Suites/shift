from enum import Enum

from botocore.config import Config
from botocore import UNSIGNED
from area import area
import pandas as pd
import zipcodes
import boto3
import os

from shift import NodeModel, ParcelModel


class RestockBuildingTypes(str, Enum):
    MULTI_FAMILY_5_PLUS_UNITS = "Multi-Family with 5+ Units"
    MULTI_FAMILY_2_4_UNITS = "Multi-Family with 2 - 4 Units"
    SINGLE_FAMILY_ATTACHED = "Single-Family Attached"
    SINGLE_FAMILY_DETACHED = "Single-Family Detached"
    MOBILE_HOME = "Mobile Home"


class ComstockBuildingTypes(str, Enum):
    QUICK_SERVICE_RESTAURANT = "QuickServiceRestaurant"
    FULL_SERVICE_RESTAURANT = "FullServiceRestaurant"
    RETAIL_STANDALONE = "RetailStandalone"
    SECONDARY_SCHOOL = "SecondarySchool"
    RETAIL_STRIPMALL = "RetailStripmall"
    PRIMARY_SCHOOL = "PrimarySchool"
    MEDIUM_OFFICE = "MediumOffice"
    LARGE_OFFICE = "LargeOffice"
    SMALL_OFFICE = "SmallOffice"
    SMALL_HOTEL = "SmallHotel"
    LARGE_HOTEL = "LargeHotel"
    OUTPATIENT = "Outpatient"
    WAREHOUSE = "Warehouse"
    HOSPITAL = "Hospital"


mapped_building_type = {
    "barn": ComstockBuildingTypes.WAREHOUSE,
    "hotel": ComstockBuildingTypes.LARGE_HOTEL,
    "transportation": ComstockBuildingTypes.MEDIUM_OFFICE,
    "farm_auxiliary": ComstockBuildingTypes.RETAIL_STANDALONE,
    "commercial": ComstockBuildingTypes.WAREHOUSE,
    "university": ComstockBuildingTypes.SECONDARY_SCHOOL,
    "train_station": ComstockBuildingTypes.LARGE_OFFICE,
    "pavilion": ComstockBuildingTypes.WAREHOUSE,
    "storage_tank": ComstockBuildingTypes.WAREHOUSE,
    "service": ComstockBuildingTypes.RETAIL_STRIPMALL,
    "retail": ComstockBuildingTypes.RETAIL_STRIPMALL,
    "religious": ComstockBuildingTypes.LARGE_OFFICE,
    "grandstand": ComstockBuildingTypes.SMALL_HOTEL,
    "college": ComstockBuildingTypes.SECONDARY_SCHOOL,
    "greenhouse": ComstockBuildingTypes.SMALL_OFFICE,
    "garages": ComstockBuildingTypes.SMALL_HOTEL,
    "construction": ComstockBuildingTypes.WAREHOUSE,
    "carport": ComstockBuildingTypes.SMALL_HOTEL,
    "garage": ComstockBuildingTypes.SMALL_HOTEL,
    "library": ComstockBuildingTypes.LARGE_OFFICE,
    "gym": ComstockBuildingTypes.RETAIL_STANDALONE,
    "school": ComstockBuildingTypes.PRIMARY_SCHOOL,
    "roof": ComstockBuildingTypes.SMALL_OFFICE,
    "skywalk": ComstockBuildingTypes.SMALL_HOTEL,
    "church": ComstockBuildingTypes.LARGE_HOTEL,
    "industrial": ComstockBuildingTypes.WAREHOUSE,
    "civic": ComstockBuildingTypes.LARGE_OFFICE,
    "hanger": ComstockBuildingTypes.SMALL_OFFICE,
    "hangar": ComstockBuildingTypes.SMALL_OFFICE,
    "bridge": ComstockBuildingTypes.SMALL_OFFICE,
    "warehouse": ComstockBuildingTypes.WAREHOUSE,
    "ruins": ComstockBuildingTypes.SMALL_OFFICE,
    "parking": ComstockBuildingTypes.SMALL_OFFICE,
    "hospital": ComstockBuildingTypes.HOSPITAL,
    "stadium": ComstockBuildingTypes.LARGE_HOTEL,
    "office": ComstockBuildingTypes.MEDIUM_OFFICE,
    "stands": ComstockBuildingTypes.SMALL_HOTEL,
    "no": ComstockBuildingTypes.SMALL_OFFICE,
    "hospital": ComstockBuildingTypes.HOSPITAL,
    "semidetached_house": RestockBuildingTypes.SINGLE_FAMILY_DETACHED,
    "residential": RestockBuildingTypes.SINGLE_FAMILY_ATTACHED,
    "dormitory": RestockBuildingTypes.MULTI_FAMILY_5_PLUS_UNITS,
    "apartments": RestockBuildingTypes.MULTI_FAMILY_2_4_UNITS,
    "detatched": RestockBuildingTypes.SINGLE_FAMILY_DETACHED,
    "fraternity": RestockBuildingTypes.MULTI_FAMILY_2_4_UNITS,
    "detached": RestockBuildingTypes.SINGLE_FAMILY_DETACHED,
    "house": RestockBuildingTypes.SINGLE_FAMILY_DETACHED,
    "yes": RestockBuildingTypes.SINGLE_FAMILY_DETACHED,
    "gatehouse": RestockBuildingTypes.MOBILE_HOME,
    "houseboat": RestockBuildingTypes.MOBILE_HOME,
    "boathouse": RestockBuildingTypes.MOBILE_HOME,
    "cabin": RestockBuildingTypes.MOBILE_HOME,
    "shed": RestockBuildingTypes.MOBILE_HOME,
}


class StockProfile(Enum):
    RESSTOCK = "resstock"
    COMSTOCK = "comstock"


class StockProfiler:
    metadata = {
        "resstock": "nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2021/resstock_amy2018_release_1/metadata/metadata.parquet",
        "comstock": "nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2021/comstock_amy2018_release_1/metadata/metadata.parquet",
    }
    profile = {
        "resstock": "nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2021/resstock_amy2018_release_1/timeseries_individual_buildings/by_county/upgrade=0/county=",
        "comstock": "nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2021/comstock_amy2018_release_1/timeseries_individual_buildings/by_county/upgrade=0/county=",
    }

    def __init__(self, profile_type: StockProfile, zip_code: str):
        self.data = pd.DataFrame()
        self.profile_type = profile_type.value
        self.zip_code = zip_code
        self.bucket_name = "oedi-data-lake"
        # Equivalent to --no-sign-request
        s3_resource = boto3.resource("s3", config=Config(signature_version=UNSIGNED))
        self.bucket = s3_resource.Bucket(self.bucket_name)

        # Download metadata file if it does not exist
        if not os.path.exists(f"{self.profile_type}.parquet"):
            print("Downloading metadata file")
            self.download_metadata()
            print("Download complete")
        else:
            print("Using existing metadata file")

        self.com_meta = pd.read_parquet(f"{self.profile_type}.parquet")
        print(f"{self.zip_code=}")
        exact_zip = zipcodes.matching(str(self.zip_code))[0]
        loc_county = exact_zip["county"]
        loc_state = exact_zip["state"]

        tag = f"{loc_state}, {loc_county}"
        filtered_meta = self.com_meta[self.com_meta["in.resstock_county_id"] == tag]
        filtered_meta.to_csv(f"filtered_meta_{self.profile_type}.csv")

    def download_metadata(self):
        aws_path = self.metadata[self.profile_type]

        for obj in self.bucket.objects.filter(Prefix=aws_path):
            file_path = f"{self.profile_type}.parquet"
            self.bucket.download_file(obj.key, file_path)

    def create_load_profiles(self, node: NodeModel, parcel: ParcelModel):
        uuid = node.name
        building_type = parcel.building_type
        print(parcel.geometry)
        obj = {
            "type": "Polygon",
            "coordinates": [[[loc.longitude, loc.latitude] for loc in parcel.geometry]],
        }
        area_sq_ft = area(obj) * 10.7639

        try:
            exact_zip = zipcodes.matching(parcel.postal_address)[0]
        except:
            exact_zip = zipcodes.matching(self.zip_code)[0]
        print(f"{exact_zip=}")
        loc_county = exact_zip["county"]
        loc_state = exact_zip["state"]

        tag = f"{loc_state}, {loc_county}"
        filtered_meta = self.com_meta[self.com_meta["in.resstock_county_id"] == tag]
        filtered_meta.to_csv(f"filtered_meta_{self.profile_type}.csv")
        if filtered_meta.empty:
            filtered_meta = self.com_meta

        try:
            filtered_meta_a = filtered_meta[
                filtered_meta["in.building_type"] == mapped_building_type[building_type].value
            ]
        except:
            filtered_meta_a = filtered_meta[
                filtered_meta["in.geometry_building_type_recs"]
                == mapped_building_type[building_type].value
            ]

        covered_area = []
        area_filter = (
            "in.geometry_floor_area"
            if "in.geometry_floor_area" in filtered_meta_a.columns
            else "in.sqft"
        )

        for area_bin in filtered_meta_a[area_filter]:
            if "-" in str(area_bin):
                area_min, area_max = area_bin.split("-")
                covered_area.append((float(area_min) + float(area_max)) / 2)
            else:
                area_bin = str(area_bin).replace("+", "")
                covered_area.append(float(area_bin))
        filtered_meta_a["area"] = covered_area
        filtered_meta_a = filtered_meta_a.iloc[
            (filtered_meta_a["area"] - area_sq_ft).abs().argsort()[:2]
        ]

        if not filtered_meta_a.empty:
            selected_profile = filtered_meta_a.sample()
        else:
            selected_profile = filtered_meta.sample()
        building_id = selected_profile.index[0]
        county = selected_profile["in.county"].to_list()[0]
        return self.download_profiles(county, building_id, uuid)

    def download_profiles(self, zipcode, building_id, uuid=None):
        path = self.profile[self.profile_type]
        aws_path = f"{path}{zipcode}/{building_id}-0.parquet"
        file_path = f"{building_id}.parquet"
        if not os.path.exists(file_path):
            print(f"Downloading file: {file_path} from zip code {zipcode}")
            print(f"AWS path: {aws_path}")
            for obj in self.bucket.objects.filter(Prefix=aws_path):
                a = self.bucket.download_file(obj.key, file_path)
        profile_data = pd.read_parquet(file_path)
        load = profile_data["out.electricity.total.energy_consumption"]
        load.index = profile_data["timestamp"]
        self.data[uuid] = load
        return load.to_list()


# profiler = StockProfiler(StockProfile.RESSTOCK, "10009")
# resstock_uuids = {
#     28744 : uuid4(),
#     31887 : uuid4(),
#     32228 : uuid4(),
#     105884 : uuid4(),
#     109796 : uuid4(),
#     114753 : uuid4(),
#     114903 : uuid4(),
#     151327 : uuid4(),
#     164419 : uuid4(),
#     172087 : uuid4(),
#     216711 : uuid4(),
#     242113 : uuid4(),
#     267713 : uuid4(),
#     475019 : uuid4(),
#     495160 : uuid4(),

# }
# for building_id, uuid in resstock_uuids.items():
#     resstock_profiles = profiler.download_profiles("G3600610", building_id, uuid)
# profiler.data.to_csv("resstock_profiles.csv")


# profiler = StockProfiler(StockProfile.COMSTOCK, "10009")
# comstock_uuids = {
#     416 : uuid4(),
#     5421 : uuid4(),
#     13270 : uuid4(),
#     # 16336 : uuid4(),
#     # 23923 : uuid4(),
#     # 27296 : uuid4(),
#     # 30614 : uuid4(),
#     # 31632 : uuid4(),
#     # 32931 : uuid4(),
#     # 33787 : uuid4(),
#     # 36784 : uuid4(),
#     # 37910 : uuid4(),
#     # 38928 : uuid4(),
#     # 42592 : uuid4(),
#     # 46928 : uuid4(),
#     # 48883 : uuid4(),
#     # 50403 : uuid4(),
#     # 51190 : uuid4(),
#     # 52576 : uuid4(),
#     # 54771 : uuid4(),
#     # 56400 : uuid4(),
#     # 57888 : uuid4(),
#     # 65302 : uuid4(),
#     # 66899 : uuid4(),
#     # 67917 : uuid4(),
#     # 70723 : uuid4(),
#     # 74672 : uuid4(),
#     # 80544 : uuid4(),
#     # 81888 : uuid4(),
#     # 82195 : uuid4(),
#     # 83408 : uuid4(),
#     # 85261 : uuid4(),
#     # 88512 : uuid4(),
#     # 93174 : uuid4(),
#     # 98115 : uuid4(),
#     # 98765 : uuid4(),
#     # 102621 : uuid4(),
#     # 105667 : uuid4(),
#     # 107155 : uuid4(),
#     # 107280 : uuid4(),
#     # 109360 : uuid4(),
#     # 110221 : uuid4(),
#     # 111491 : uuid4(),
#     # 112166 : uuid4(),
#     # 113216 : uuid4(),
#     # 114736 : uuid4(),
#     # 117139 : uuid4(),
#     # 120963 : uuid4(),
#     # 124627 : uuid4(),
#     # 125645 : uuid4(),
#     # 130013 : uuid4(),
#     # 130688 : uuid4(),
#     # 131757 : uuid4(),
#     # 133744 : uuid4(),
#     # 138112 : uuid4(),
#     # 138541 : uuid4(),
#     # 139171 : uuid4(),
#     # 139763 : uuid4(),
#     # 145997 : uuid4(),
#     # 150259 : uuid4(),
#     # 154595 : uuid4(),
#     # 157107 : uuid4(),
#     # 158125 : uuid4(),
#     # 159872 : uuid4(),
#     # 160275 : uuid4(),
#     # 163104 : uuid4(),
#     # 165158 : uuid4(),
#     # 165427 : uuid4(),
#     # 167824 : uuid4(),
#     # 169763 : uuid4(),
#     # 171680 : uuid4(),
#     # 172240 : uuid4(),
#     # 175318 : uuid4(),
#     # 180851 : uuid4(),
#     # 183917 : uuid4(),
#     # 189584 : uuid4(),
#     # 190614 : uuid4(),
#     # 191795 : uuid4(),
#     # 193952 : uuid4(),
#     # 195619 : uuid4(),
#     # 197571 : uuid4(),
#     # 197645 : uuid4(),
#     # 202614 : uuid4(),
#     # 203632 : uuid4(),
#     # 206144 : uuid4(),
#     # 207142 : uuid4(),
#     # 209968 : uuid4(),
#     # 216640 : uuid4(),
#     # 217910 : uuid4(),
#     # 220976 : uuid4(),
#     # 221568 : uuid4(),
#     # 225779 : uuid4(),
#     # 228470 : uuid4(),
#     # 230144 : uuid4(),
#     # 232259 : uuid4(),
#     # 234480 : uuid4(),
#     # 235085 : uuid4(),
#     # 236115 : uuid4(),
#     # 237990 : uuid4(),
#     # 238595 : uuid4(),
#     # 241846 : uuid4(),
#     # 244912 : uuid4(),
#     # 248486 : uuid4(),
#     # 252854 : uuid4(),
#     # 253459 : uuid4(),
#     # 254019 : uuid4(),
#     # 254806 : uuid4(),
#     # 256512 : uuid4(),
#     # 257117 : uuid4(),
#     # 258387 : uuid4(),
#     # 259318 : uuid4(),
#     # 260336 : uuid4(),
#     # 262310 : uuid4(),
#     # 263427 : uuid4(),
#     # 264291 : uuid4(),
#     # 266678 : uuid4(),
#     # 269744 : uuid4(),
#     # 271360 : uuid4(),
# }
# for building_id, uuid in comstock_uuids.items():
#     comstock_profiles = profiler.download_profiles("G3600610", building_id, uuid)
# profiler.data.to_csv("comstock_profiles.csv")

# # node = NodeModel(
# #     name='b82a3db4-93ed-487e-853a-f3d615c169c8',
# #     location=Location(name='', x=-104.96553092306591, y=39.72389874711931, crs='epsg:4326'),
# #     assets={DistributionLoad}
# # )

# # parcel = ParcelModel(
# #     name='parcel_54',
# #     geometry=[
# #         GeoLocation(longitude=-104.9655986, latitude=39.7240747), GeoLocation(longitude=-104.965555, latitude=39.7240745),
# #         GeoLocation(longitude=-104.9655548, latitude=39.7241174), GeoLocation(longitude=-104.9655317, latitude=39.7241173),
# #         GeoLocation(longitude=-104.9655317, latitude=39.7241205), GeoLocation(longitude=-104.9654104, latitude=39.7241201),
# #         GeoLocation(longitude=-104.9654107, latitude=39.7240597), GeoLocation(longitude=-104.9654379, latitude=39.7240597),
# #         GeoLocation(longitude=-104.9654384, latitude=39.7239751), GeoLocation(longitude=-104.9654298, latitude=39.7239751),
# #         GeoLocation(longitude=-104.9654298, latitude=39.7239609), GeoLocation(longitude=-104.9654368, latitude=39.7239609),
# #         GeoLocation(longitude=-104.9654373, latitude=39.7238607), GeoLocation(longitude=-104.9654467, latitude=39.7238607),
# #         GeoLocation(longitude=-104.965597, latitude=39.7238612), GeoLocation(longitude=-104.9655969, latitude=39.7238858),
# #         GeoLocation(longitude=-104.9656313, latitude=39.7238859), GeoLocation(longitude=-104.965631, latitude=39.723936),
# #         GeoLocation(longitude=-104.9655974, latitude=39.7239359), GeoLocation(longitude=-104.965597, latitude=39.7239965),
# #         GeoLocation(longitude=-104.9656297, latitude=39.7239966), GeoLocation(longitude=-104.9656295, latitude=39.7240458),
# #         GeoLocation(longitude=-104.9655988, latitude=39.7240457), GeoLocation(longitude=-104.9655986, latitude=39.7240747)
# #         ],
# #     building_type='residential',
# #     city='Denver',
# #     state='CO',
# #     postal_address='80218',
# # )
