""" CSV MODULE IMPORT"""
import csv
import sys

from datetime import datetime

# class RowCounters:
#     """ Object which holds different types of counters"""
#     def __init__(self) -> None:
#         self.serial_ctr = 0
#         self.gen_hu_ctr = 0

class NumbersProfile:
    """ Class for holding numbers profiles """
    def __init__(self, length: int, start_value: int, prefix: str) -> None:
        self.length = length
        self.number = start_value-1
        self.prefix = prefix

    def get_next_number_as_string(self, padding: bool = True) -> str:
        """ Next number profile """
        paddingstr = ""
        suffix = self.get_next_suffix_value()

        if padding:
            paddingstr = "0" * (self.length - len(self.prefix) - len(suffix))

        string = self.prefix + paddingstr + str(self.number)

        return string

    def get_next_suffix_value(self) -> str:
        """ Next suffix number """
        self.number += 1
        return str(self.number)

class StockUploadConfig:
    """ Setting the configuration of how the stock upload should be done. """
    def __init__(self, name: str = "",                  \
                 standard_bin: str = "",                \
                 record_hu: bool = False,               \
                 record_quant: bool = False,            \
                 consider_bin: bool = False,            \
                 consider_serial: bool = False,         \
                 generate_serial: bool = False,         \
                 generate_hu: bool = False,             \
                 ) -> None:

        self.name = name
        self.standard_bin = standard_bin
        self.row = 1
        self.record_quant = record_quant
        self.record_hu = record_hu
        self.consider_bin = consider_bin
        self.consider_serial = consider_serial
        self.generate_serial = generate_serial
        self.generate_hu = generate_hu

class PeriphiralData:
    """ Objcet which passes data, for e.g. blocks and qty per hu """
    def __init__(self, blocks: dict, qty_per_hu: dict) -> None:
        self.blocks = blocks
        self.qty_per_hu = qty_per_hu

final_file_title_conv = {
    "MANDT": 0,
    "POSTYPE": 1,
    "MATNR": 2,
    "OWNER": 3,
    "OWNER_ROLE": 4,
    "BATCH": 5,
    "CAT": 6,
    "STOCK_DOCCAT": 7,
    "STOCK_DOCNO": 8,
    "STOCK_ITMNO": 9,
    "STOCK_USAGE": 10,
    "ENTITELED": 11,
    "ENTITLED_ROLE": 12,
    "COO": 13,
    "QUAN": 14,
    "UNIT": 15,
    "HUTYP": 16,
    "LGPLA": 17,
    "GR_DATE": 18,
    "GR_TIME": 19,
    "VFDAT": 20,
    "PMAT": 21,
    "EXTNO": 22,
    "HUIDENT": 23,
    "PARHUIDENT": 24,
    "TOPHUIDENT": 25,
    "ROW": 26,
    "REFROW": 27,
    "G_WEIGHT": 28,
    "N_WEIGHT": 29,
    "UNIT_GW": 30,
    "T_WEIGHT": 31,
    "UNIT_TW": 32,
    "G_VOLUME": 33,
    "N_VOLUME": 34,
    "UNIT_GV": 35,
    "T_VOLUME": 36,
    "UNIT_TV": 37,
    "G_CAPA": 38,
    "N_CAPA": 39,
    "T_CAPA": 40,
    "LENGTH": 41,
    "WIDTH": 42,
    "HEIGHT": 43,
    "UNIT_LWH": 44,
    "MAX_WEIGHT": 45,
    "TOLW": 46,
    "TARE_VAR": 47,
    "MAX_VOLUME": 48,
    "TOLV": 49,
    "CLOSED_PACKAGE": 50,
    "MAX_CAPA": 51,
    "MAX_LENGTH": 52,
    "MAX_WIDTH": 53,
    "MAX_HEIGHT": 54,
    "UNIT_MAX_LWH": 55,
    "SERNR": 56,
    "CWQUAN": 57,
    "CWUNIT": 58,
    "CWEXACT": 59,
    "LOGPOS": 60,
    "UII": 61,
    "DUMMY_ISU": 62,
    "ZEUGN": 63,
    "AMOUNT_LC": 64 
}

final_row_length = len(final_file_title_conv.keys())

def get_blocks_from_file(file_name: str, relevant_blocks: list[str]) -> dict:
    """ Get all the blockings inside a dictionary """
    blocks = {}

    with open(file_name, "r", encoding="UTF-8-SIG") as file:
        reader = csv.reader(file, delimiter=DELIMITER)
        _ = str(next(reader))

        for row in reader:
            hu = row[0] + row[1]
            block_type = row[3]

            if block_type not in relevant_blocks:
                continue

            existing_key = blocks.get(hu)
            if existing_key is not None:
                blocks[hu].append(block_type)
            else:
                blocks[hu] = [block_type]


    return blocks

def get_stock_and_bin(hu: str, hu_blocks: dict, standard_bin: str):
    """ Get stock type and bin if hu is blocked or not. Is only relevant in high bay. """
    stock_type = ""
    ewm_bin = ""

    blocked_hu = hu_blocks.get(hu)

    if blocked_hu:
        sparr_to_stock_type = {
            'O': {
                "stock_type" : "B2",
                "bin": "??REPACK BIN??"},
            'K': {
                "stock_type": "B2",
                "bin": standard_bin },
            'S': {
                "stock_type": "B2",
                "bin": standard_bin}
        }

        stock_type = sparr_to_stock_type[blocked_hu[0]]["stock_type"]
        ewm_bin = sparr_to_stock_type[blocked_hu(hu)[0]]["bin"]
    else:
        stock_type = STANDARD_CAT
        ewm_bin = standard_bin

    return stock_type, ewm_bin

def get_hu_number(length: int, prefix: str, suffix: str) -> tuple[str, str]:
    """ returns a hu number based on the total length (HU_LENGTH),  \
        the prefix (VENDOR) and suffix (PACKAGE ID)                 \
        - padding done in the middle with 0:s normal HU             \
        The short number is also returned as its needed for e.g.    \
        looking into the blocking """

    hu_padding = "0" * (length-len(prefix)-len(suffix))
    hu_short = prefix + suffix
    hu = prefix + hu_padding + suffix

    # superprefix = ""

    # if prefix[0].isdigit:
    #     superprefix = "'"

    return hu, hu_short

def create_entry_per_hu(input_row: list[str],                       \
                        config: StockUploadConfig,                  \
                        data: PeriphiralData,                       \
                        gen_serial_numbers: NumbersProfile,  \
                        gen_hu_numbers: NumbersProfile       \
                            ) -> list[dict]:

    """ Creates necessary entries for an HU, from a raw source """

    if config.consider_serial and gen_serial_numbers == 0:
        print("Serialized true, and no serial number suffix. Please rectify.")
        quit()

    hu, hu_short = get_hu_number(gen_hu_numbers.length, input_row[0], input_row[1])

    hutype          = input_row[6]
    material        = input_row[5]
    quantity        = input_row[7]
    grdate          = input_row[2]
    grtime          = input_row[3]
    # serial_number   = input_row[9]
    ref_row         = -1
    stock_type      = ""
    ewm_bin         = ""

    if config.consider_bin is False:
        stock_type, ewm_bin = get_stock_and_bin(hu_short, data.blocks, config.standard_bin)
    else:
        ewm_bin = input_row[4]
        stock_type = STANDARD_CAT

    return_list = []

    if len(quantity) == 0:
        quantity = 0

    if int(quantity) < 1:
        return return_list

    if config.record_hu:
        row = []

        for _ in range(len(final_file_title_conv)):
            row.append("")

        row[final_file_title_conv["MANDT"]]            = STANDARD_MANDT
        row[final_file_title_conv["POSTYPE"]]          = "1"
        row[final_file_title_conv["HUIDENT"]]          = hu
        row[final_file_title_conv["LGPLA"]]            = ewm_bin
        row[final_file_title_conv["HUTYP"]]            = hutype
        row[final_file_title_conv["TOPHUIDENT"]]       = hu
        row[final_file_title_conv["PMAT"]]             = STANDARD_PMAT
        row[final_file_title_conv["EXTNO"]]            = "X"
        row[final_file_title_conv["ROW"]]              = str(config.row)

        config.row += 1
        return_list.append(row)

    qty_per_hu = 0
    int_qty = int(quantity)

    if config.generate_hu:
        qty_per_hu = int(data.qty_per_hu.get(material, 0))

    if config.generate_hu and qty_per_hu > 0:
        # new_hu_ctr = math.ceil(int(quantity)/qty_per_hu)
        while int_qty > 0:
            new_hu_qty = min(int_qty, qty_per_hu)

            row = []

            for _ in range(len(final_file_title_conv)):
                row.append("")

            generated_hu = gen_hu_numbers.get_next_number_as_string()

            row[final_file_title_conv["MANDT"]]            = STANDARD_MANDT
            row[final_file_title_conv["POSTYPE"]]          = "2"
            row[final_file_title_conv["HUIDENT"]]          = generated_hu
            row[final_file_title_conv["LGPLA"]]            = ewm_bin
            row[final_file_title_conv["HUTYP"]]            = hutype
            row[final_file_title_conv["TOPHUIDENT"]]       = hu
            row[final_file_title_conv["PMAT"]]             = STANDARD_PMAT
            row[final_file_title_conv["EXTNO"]]            = "X"
            row[final_file_title_conv["ROW"]]              = str(config.row)

            config.row += 1
            return_list.append(row)

            row = []

            for _ in range(len(final_file_title_conv)):
                row.append("")

            row[final_file_title_conv["MANDT"]]            = STANDARD_MANDT
            row[final_file_title_conv["POSTYPE"]]          = "4"
            row[final_file_title_conv["MATNR"]]            = material
            row[final_file_title_conv["OWNER"]]            = STANDARD_OWNER
            row[final_file_title_conv["OWNER_ROLE"]]       = STANDARD_OWNER_ROLE
            row[final_file_title_conv["CAT"]]              = stock_type
            row[final_file_title_conv["ENTITELED"]]        = STANDARD_ENTITELED
            row[final_file_title_conv["ENTITLED_ROLE"]]    = STANDARD_ENTITLED_ROLE
            row[final_file_title_conv["QUAN"]]             = str(new_hu_qty)
            row[final_file_title_conv["UNIT"]]             = STANDARD_UNIT
            row[final_file_title_conv["LGPLA"]]            = ewm_bin
            row[final_file_title_conv["GR_DATE"]]          = grdate
            row[final_file_title_conv["GR_TIME"]]          = grtime
            row[final_file_title_conv["VFDAT"]]            = grdate
            row[final_file_title_conv["HUIDENT"]]          = generated_hu
            row[final_file_title_conv["TOPHUIDENT"]]       = hu
            row[final_file_title_conv["ROW"]]              = str(config.row)

            ## Used for referencing higher level of HU for the serials later on
            ref_row = row[final_file_title_conv["ROW"]]

            return_list.append(row)

            config.row += 1
            int_qty -= qty_per_hu

    elif config.record_quant:
        row = []

        for _ in range(len(final_file_title_conv)):
            row.append("")

        row[final_file_title_conv["MANDT"]]            = STANDARD_MANDT
        row[final_file_title_conv["POSTYPE"]]          = "4"
        row[final_file_title_conv["MATNR"]]            = material
        row[final_file_title_conv["OWNER"]]            = STANDARD_OWNER
        row[final_file_title_conv["OWNER_ROLE"]]       = STANDARD_OWNER_ROLE
        row[final_file_title_conv["CAT"]]              = stock_type
        row[final_file_title_conv["ENTITELED"]]        = STANDARD_ENTITELED
        row[final_file_title_conv["ENTITLED_ROLE"]]    = STANDARD_ENTITLED_ROLE
        row[final_file_title_conv["QUAN"]]             = quantity
        row[final_file_title_conv["UNIT"]]             = STANDARD_UNIT
        row[final_file_title_conv["LGPLA"]]            = ewm_bin
        row[final_file_title_conv["GR_DATE"]]          = grdate
        row[final_file_title_conv["GR_TIME"]]          = grtime
        row[final_file_title_conv["VFDAT"]]            = grdate
        row[final_file_title_conv["HUIDENT"]]          = hu
        row[final_file_title_conv["TOPHUIDENT"]]       = hu
        row[final_file_title_conv["ROW"]]              = str(config.row)

        ## Used for referencing higher level of HU for the serials later on
        ref_row = row[final_file_title_conv["ROW"]]

        config.row += 1
        return_list.append(row)
    
    # if config.record_serial:


    if config.generate_serial:
        for i in range(int(quantity)):
            row = []

            ser_nr = gen_serial_numbers.get_next_number_as_string()

            for _ in range(len(final_file_title_conv)):
                row.append("")

            row[final_file_title_conv["MANDT"]]         = STANDARD_MANDT
            row[final_file_title_conv["POSTYPE"]]       = "6"
            row[final_file_title_conv["ROW"]]           = str(config.row)
            row[final_file_title_conv["SERNR"]]         = ser_nr

            if ref_row == -1:
                row[final_file_title_conv["REFROW"]]    = row[final_file_title_conv["ROW"]]
            else:
                row[final_file_title_conv["REFROW"]]    = str(ref_row)

            config.row += 1
            return_list.append(row)

            # !!! Limit number of rows due to performance   !!!
            # !!! need to be removed when used in practice  !!!
            if i > 5:
                break

    return return_list

def create_entry_per_serial(input_row: list[str], config: StockUploadConfig, data: PeriphiralData):
    ser_nr = input_row[9]

    return_list = []

    row = []

    for _ in range(len(final_file_title_conv)):
        row.append("")

    row[final_file_title_conv["MANDT"]]         = STANDARD_MANDT
    row[final_file_title_conv["POSTYPE"]]       = "6"
    row[final_file_title_conv["ROW"]]           = str(config.row)
    row[final_file_title_conv["SERNR"]]         = ser_nr

    return return_list

def create_stock_upload_file(file_name: str,                        \
                             config: StockUploadConfig,             \
                             data: PeriphiralData,                  \
                             gen_serial_numbers: NumbersProfile,    \
                             gen_hu_numbers: NumbersProfile) -> None:

    """ Main function for creating the final file """
    with open(file_name, "r", encoding="UTF-8-SIG") as file:
        reader                      = csv.reader(file, delimiter=DELIMITER)
        first_row                   = str(next(reader))

        titles = first_row.split(DELIMITER)
        titles_dictionary = {}

        for idx, title in enumerate(titles):
            titles_dictionary[idx] = title

        final_entries = []

        for _, row in enumerate(reader):
            if config.consider_serial is False:
                entries = create_entry_per_hu(
                    input_row = row,                                   \
                    config=config,                                     \
                    data=data,                                         \
                    gen_serial_numbers=gen_serial_numbers,             \
                    gen_hu_numbers=gen_hu_numbers)

            elif config.consider_serial and len(row[9]) > 0:
                entries = create_entry_per_serial(input_row = row, config=config, data=data)

            for entry in entries:
                final_entries.append(entry)

    current_date_time = datetime.now()
    current_date_time_str = current_date_time.strftime("%Y%m%d%H%M%S")
    folder = "upload_files/"
    target_file = f"{folder}stock_upload_{config.name}_{current_date_time_str}.csv"

    with open(target_file, "w", encoding="UTF-8-SIG", newline='') as file:
        writer = csv.writer(file, delimiter=DELIMITER)
        writer.writerow(final_file_title_conv.keys())
        writer.writerows(final_entries)

        print(f"A new file was successfully written: {target_file} \
              Number of rows: {len(final_entries)}")


def get_qty_per_hu_from_file(file_name: str) -> dict:
    """ Get information about how many pieces are inside one HU """
    mat_hu_qty = {}

    with open(file_name, "r", encoding="UTF-8-SIG") as file:
        reader = csv.reader(file, delimiter=DELIMITER)
        _ = str(next(reader))

        for row in reader:
            material = row[0]
            qty = row[1]

            existing_key = mat_hu_qty.get(material)
            if existing_key is None:
                mat_hu_qty[material] = qty
            else:
                print("Duplicate material found, " \
                      +"please look into source file for material and hu qty")
                sys.exit()

    return mat_hu_qty 

DELIMITER               = ","

STANDARD_PMAT           = "8289999"
STANDARD_OWNER          = "BP1101EWM"
STANDARD_OWNER_ROLE     = "BP"
STANDARD_CAT            = "F2"
STANDARD_ENTITELED      = "BP1101EWM"
STANDARD_ENTITLED_ROLE  = "BP"
STANDARD_UNIT           = "PCE"
STANDARD_MANDT          = "100"

RELEVANT_BLOCK_TYPES    = ['O', 'K', "S"]

BLOCK_DATA_FILE         = "legacy_block.csv"    # File must exist inside source folder
MAT_QTY_PER_HU_FILE     = "mat_qty_per_hu.csv"  # File must exist inside source folder
SOURCE_FILE             = "legacy_stock_test_serials.csv"    # File must exist inside source folder

blocks_dict = get_blocks_from_file(BLOCK_DATA_FILE, RELEVANT_BLOCK_TYPES)
mat_hu_qty_dict = get_qty_per_hu_from_file(MAT_QTY_PER_HU_FILE)

periphiral_data = PeriphiralData(blocks_dict, mat_hu_qty_dict)

gen_serial_numbers = NumbersProfile(length=10, start_value=1, prefix='S')
gen_hu_numbers = NumbersProfile(length=14, start_value=900000000, prefix="00000")


config_high_bay = StockUploadConfig(
    name                = "high_bay",
    standard_bin        = "HIGH BAY BIN",
    record_quant        = True,
    record_hu           = True,
    consider_bin        = False,
    consider_serial     = False,
    generate_serial     = False,
    generate_hu         = True,
)

config_plm3 = StockUploadConfig(
    name                = "plm3",
    record_quant        = True,
    record_hu           = True,
    consider_bin        = True,
    consider_serial     = False,
    generate_serial     = False,
    generate_hu         = False,
)

config_o_blanks = StockUploadConfig(
    name                = "o_blanks",
    record_quant        = True,
    record_hu           = True,
    consider_bin        = False,
    consider_serial     = False,
    generate_serial     = True,
    generate_hu         = False,
)

config_ks1j = StockUploadConfig(
    name                = "ks1j",
    standard_bin        = "KS1J_BIN",
    record_quant        = True,
    record_hu           = False,
    consider_bin        = False,
    consider_serial     = True,
    generate_serial     = False,
    generate_hu         = False,
)


# CHANGE config= PARAMETER TO TRIGGER CORRECT UPLOAD CONVERTION
# Possible config= s:
# confing_high_bay      // used for stock inside high bay
# config_plm3           // used for stock inside plm3   
# config_blanks         // used for stock at inbound blanks
# config_psa            // used for stock at line side
# config_               // ... more

create_stock_upload_file(SOURCE_FILE,                           \
                         config=config_high_bay,                \
                         data=periphiral_data,                  \
                         gen_serial_numbers=gen_serial_numbers, \
                         gen_hu_numbers=gen_hu_numbers)
