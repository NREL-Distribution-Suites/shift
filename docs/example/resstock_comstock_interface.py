from enum import Enum
from pathlib import Path

from botocore.config import Config
from botocore import UNSIGNED
from area import area
import pandas as pd
import zipcodes
import boto3

from shift import NodeModel, ParcelModel

BUILD_DIR = Path(__file__).resolve().parent / "_build"
BUILD_DIR.mkdir(parents=True, exist_ok=True)


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
        self.metadata_path = BUILD_DIR / f"{self.profile_type}.parquet"
        # Equivalent to --no-sign-request
        s3_resource = boto3.resource("s3", config=Config(signature_version=UNSIGNED))
        self.bucket = s3_resource.Bucket(self.bucket_name)

        # Download metadata file if it does not exist
        if not self.metadata_path.exists():
            print("Downloading metadata file")
            self.download_metadata()
            print("Download complete")
        else:
            print("Using existing metadata file")

        self.com_meta = pd.read_parquet(self.metadata_path)
        print(f"{self.zip_code=}")
        exact_zip = zipcodes.matching(str(self.zip_code))[0]
        loc_county = exact_zip["county"]
        loc_state = exact_zip["state"]

        tag = f"{loc_state}, {loc_county}"
        filtered_meta = self.com_meta[self.com_meta["in.resstock_county_id"] == tag]
        filtered_meta.to_csv(BUILD_DIR / f"filtered_meta_{self.profile_type}.csv")

    def download_metadata(self):
        aws_path = self.metadata[self.profile_type]

        for obj in self.bucket.objects.filter(Prefix=aws_path):
            self.bucket.download_file(obj.key, str(self.metadata_path))

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
        except (IndexError, TypeError, KeyError):
            exact_zip = zipcodes.matching(self.zip_code)[0]
        print(f"{exact_zip=}")
        loc_county = exact_zip["county"]
        loc_state = exact_zip["state"]

        tag = f"{loc_state}, {loc_county}"
        filtered_meta = self.com_meta[self.com_meta["in.resstock_county_id"] == tag]
        filtered_meta.to_csv(BUILD_DIR / f"filtered_meta_{self.profile_type}.csv")
        if filtered_meta.empty:
            filtered_meta = self.com_meta

        normalized_type = (building_type or "").strip().lower()
        supported_building_type = mapped_building_type.get(normalized_type)
        if supported_building_type is None:
            supported_building_type = (
                RestockBuildingTypes.SINGLE_FAMILY_DETACHED
                if self.profile_type == StockProfile.RESSTOCK.value
                else ComstockBuildingTypes.WAREHOUSE
            )

        if "in.building_type" in filtered_meta.columns:
            filtered_meta_a = filtered_meta[
                filtered_meta["in.building_type"] == supported_building_type.value
            ]
        elif "in.geometry_building_type_recs" in filtered_meta.columns:
            filtered_meta_a = filtered_meta[
                filtered_meta["in.geometry_building_type_recs"] == supported_building_type.value
            ]
        else:
            filtered_meta_a = filtered_meta

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
        file_path = BUILD_DIR / f"{building_id}.parquet"
        if not file_path.exists():
            print(f"Downloading file: {file_path} from zip code {zipcode}")
            print(f"AWS path: {aws_path}")
            for obj in self.bucket.objects.filter(Prefix=aws_path):
                self.bucket.download_file(obj.key, str(file_path))
        profile_data = pd.read_parquet(file_path)
        load = profile_data["out.electricity.total.energy_consumption"]
        load.index = profile_data["timestamp"]
        self.data[uuid] = load
        return load.to_list()
