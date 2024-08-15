# API Documentation

### Outline
- [API Documentation](#api-documentation)
    - [Outline](#outline)
    - [getAllData (TODO)](#getalldata-todo)
    - [calPacking](#calpacking)



### getAllData (TODO)

```
{
    "box": [
      {
        "name": "example7-Bin1",
        "WHD": [5, 5, 5],
        "weight": 100,
        "corner": 0,
        "openTop": [0]
      },
    ],
    "item": [
      {
        "name": "Box-1",
        "WHD": [5, 4, 1],
        "weight": 1,
        "level": 1,
        "loadbear": 100,
        "updown": true,
        "color": "yellow",
        "type": 1
      },
    ]
  }
  
```
# **Output Explanation**

| **Parameter Name** | **Type** | **Description** | **Details** |
|:------------------:|:-------:|:---------------:|:-----------:|
| **box**            | **Object**  | **Container Information** | **Includes name, weight, openTop, corner** |
| <font color="red">**name**</font> | **String**  | **Container Name** | Unique display name for the container |
| <font color="red">**WHD**</font>  | **Array(int)**  | **Container Dimensions** | Length, width, and height of the container |
| <font color="red">**weight**</font> | **Integer**  | **Maximum Load Capacity of the Container** | Unit is KG |
| **openTop**        | **Array**  | **Supported Opening Types of the Container** | 1 represents side opening, 2 represents top opening |
| **corner**          | **int**  | **Size of the Corner Piece** | 0 represents no corner piece, starting from 1 there is a corner piece, unit is cm |
| **item**           | **Object**  | **Item Information** | **Includes name, count, updown, type, level, loadbear, weight, color** |
| <font color="red">**name**</font> | **String**  | **Item Name** | Unique display name for the item |
| **count**          | **Integer**  | **Quantity of the Item** | Unit is pieces |
| **updown**         | **Integer**  | **Can the Item be Placed Upside Down** | 0: false, 1: true |
| <font color="red">**type**</font> | **Integer**  | **Item Shape** | 1: Cuboid, 2: Cylinder |
| **level**          | **Integer**  | **Must the Item be Boxed** | 0: false, 1: true |
| <font color="red">**loadbear**</font> | **Integer**  | **Load Bearing Capacity of the Item** | Unit is KG |
| <font color="red">**weight**</font> | **Integer**  | **Weight of the Item** | Unit is KG |
| **color**          | **Integer**  | **Display Color of the Item** | 1: Red, 2: Yellow, 3: Blue, 4: Green, 5: Purple, 6: Brown, 7: Orange |

---

### **Note**

This output structure is identical to the structure required by the front end for the calculation return.  
**Values in red font represent fields that cannot be modified by the user; other fields can be modified by the user.**

### calPacking

**Brief Description:**

- <p>Frontend sends out the cargo and container information and retrieves the calculation results</p>

**Request URL:**
- Internal `http://10.10.19.29:771/calPacking`
- External ``

**Request Method:**
- POST, GET

**Input Example**
```
{
    "box": [
        {
            "name": "40ft High Cube Container",
			"WHD" : [1203,235,269],
            "weight": 26280,
            "openTop": [1,2],
            "corner":15
        }
    ],
    "item": [
        {
            "name":"Dyson_DC34_Animal",
			"WHD" : [170,82,46],
            "count":5,
            "updown":1,
            "type":1,
            "level":0,
            "loadbear":100,
            "weight":85,
            "color" :1
        },
        {
            "name":"Panasonic_NA-V160GBS",
			"WHD" : [85,60,60],
            "count":18,
            "updown":1,
            "type":1,
            "level":0,
            "loadbear":100,
            "weight":30,
            "color" :2
        },
    ],
	"binding" : [
        [
           "Wood_Table",
           "50_Gal_Oil_Drum"
        ],
    ]
}
```
# **Input Explanation**

| **Parameter Name** | **Type** | **Description** | **Details** |
|:------------------:|:-------:|:---------------:|:-----------:|
| **box**            | **Object**  | **Container Information** | **Includes name, weight, openTop, corner** |
| **name**           | String  | Container Name | Unique display name for the container |
| **WHD**            | Array(int)  | Container Dimensions | Length, width, and height of the container |
| **weight**         | Integer  | Maximum Load Capacity of the Container | Unit is KG |
| **openTop**        | Array  | Supported Opening Types of the Container | 1 represents side opening, 2 represents top opening |
| **corner**          | int  | Size of the Corner Piece | 0 represents no corner piece, starting from 1 there is a corner piece, unit is cm |
| **item**           | **Object**  | **Item Information** | **Includes name, count, updown, type, level, loadbear, weight, color** |
| **name**           | String  | Item Name | Unique display name for the item |
| **count**          | Integer  | Quantity of the Item | Unit is pieces |
| **updown**         | Integer  | Can the Item be Placed Upside Down | 0: false, 1: true |
| **type**           | Integer  | Item Shape | 1: Cuboid, 2: Cylinder |
| **level**          | Integer  | Must the Item be Boxed | 0: false, 1: true |
| **loadbear**       | Integer  | Load Bearing Capacity of the Item | Unit is KG |
| **weight**         | Integer  | Weight of the Item | Unit is KG |
| **color**          | Integer  | Display Color of the Item | 1: Red, 2: Yellow, 3: Blue, 4: Green, 5: Purple, 6: Brown, 7: Orange |
| **binding**        | **Array**  | **Item Binding Information** | **Array** |

---

### **Note**
This input structure is intended to be used for configuring the container and items.  
Each field plays a critical role in ensuring the data is correctly processed.


**Output Example**
```
{
    "Success": true,
    "data": {
        "box": [
            {
                "WHD": [
                    1203,
                    235,
                    238
                ],
                "gravity": [
                    26.37,
                    25.95,
                    27.88,
                    19.79
                ],
                "partNumber": "40ft Steel Container",
                "position": [
                    601.5,
                    117.5,
                    119.0
                ],
                "weight": 26480
            }
        ],
        "fitItem": [
            {
                "WHD": [
                    15,
                    15,
                    15
                ],
                "color": "#000000",
                "name": "corner",
                "partNumber": "corner0",
                "position": [
                    7,
                    7,
                    7
                ],
                "rotationType": 0,
                "type": "cube",
                "weight": 0
            },
        ],
        "unfitItem": [
            {
                "WHD": [
                    152,
                    75,
                    152
                ],
                "color": "orange",
                "name": "Wood_Table",
                "partNumber": "Wood_Table-8",
                "position": [
                    76,
                    37,
                    76
                ],
                "rotationType": 5,
                "type": "cube",
                "weight": 70
            },
        ]
    }
}
```
# **Output Explanation**

| **Parameter Name** | **Type** | **Description** | **Details** |
|:------------------:|:-------:|:---------------:|:-----------:|
| **Success**        | bool     | API Call Success or Failure | `true` represents correct input and system functioning, `false` represents incorrect input or system issue |
| **data**           | Object   | Detailed Information Required by the Front End | Includes `box`, `fitItem`, `unfitItem` |
| **box**            | **Array**  | **Container Information** | **Includes `WHD`, `position`, `partNumber`, `weight`** |
| **WHD**            | Array    | Container Dimensions | First position represents length (width), second position represents width (height), third position represents height (depth) |
| **position**       | Array    | Starting Position of the Container | First position represents x, second position represents y, third position represents z |
| **partNumber**     | string   | Part Number of the Container |  |
| **weight**         | int      | Container Load Capacity | Unit is KG |
| **gravity**        | Array    | Weight Distribution in Four Quarters of the Container | Unit is percentage (%) |
| **fitItem**        | **Array**  | **Information of Items that Fit in the Container** | **Includes `WHD`, `color`, `partNumber`, `position`, `rotationType`, `type`, `weight`** |
| **WHD**            | Array    | Item Dimensions | First position represents length (width), second position represents width (height), third position represents height (depth) |
| **color**          | string   | Item Color | Represented as a hexadecimal color code |
| **partNumber**     | string   | Part Number of the Item |  |
| **position**       | Array    | Starting Position of the Item | First position represents x, second position represents y, third position represents z |
| **rotationType**   | int      | Rotation Type of the Item | Six possible orientations represented by 0-5 |
| **name**           | string   | Item Type Name |  |
| **type**           | string   | Is the Item Cuboid or Cylinder | `"cube"` represents cuboid, `"cylinder"` represents cylinder |
| **weight**         | int      | Item Weight | Unit is KG |

---

### **Note**
The parameters of `unfitItem` are the same as those of `fitItem`.

