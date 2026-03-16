> PROJECT PROPOSAL
>
> Group Name: **AGRISTRESS** **AVENGERS**
>
> Group Members: **Badiya** **Sunil** **Kumar,** **Yashaswini.H** **V,**
> **SRL** **Keerthi,** **Sibbala** **Yoshitha**
>
> Project Working Title: **Spatial** **Hotspot** **Detection** **of**
> **Farmer** **Stress** **using** **Geospatial** **Farmer** **Stress**
> **Index**
>
> **1.Problem** **Statement**
>
> **Spatial** **Problem:**
>
> Climate variability, crop yield disparities, market price swings,
> irrigation availability, and cultivation costs all contribute to
> farmer stress, which is not consistent across regions. These
> indicators are often analysed separately by current agricultural
> monitoring systems, which do not take regional spatial linkages into
> account. This makes it more difficult to pinpoint geographical
> groupings, or "hotspots," of agricultural suffering. In order to
> identify high-stress agricultural areas, the proposed project would
> provide a geospatial analytical framework that combines various
> agricultural variables into a single Farmer Stress Index (FSI) and
> uses spatial hotspot identification.
>
> **Aim** **for** **Users:**
>
> • Departments of government agricultural planning • NGOs and rural
> development organizations
>
> • Policy analysts and agricultural researchers
>
> • Regional planning authority at the local level
>
> **2.** **Technical** **Stack** **&** **Libraries**
>
> **GUI** **Structure:**
>
> Streamlit for the creation of interactive web- based dashboards
>
> Fundemental Geospatial Logic:
>
> QGIS for creating thematic maps and preparing geographical data
>
> GeoPandas for analyzing and integrating geographical data
>
> For geometric operation, Shapely PySAL for hotspot identification and
> spatial statistics
>
> Advanced Part: Stress classification and grouping using machine
> learning with Scikit-learn Techniques for spatial autocorrelation like
> Getis-Ord Gi\* and Moran's I
>
> **Sources** **of** **Data:**
>
> Climate and rainfall data from publicly accessible government websites
> Statistics on crop production Datasets of agricultural market prices
> Datasets on cultivation costs Geographic coordinate data and
> shapefiles for district boundaries
>
> **3.** **Proposed** **GUI** **Architecture**
>
> **Section** **of** **Input:**
>
> Upload agricultural datasets in Excel or CSV format. Spatial boundary
> shapefiles can be uploaded.
>
> Choose indicators to calculate the Farmer Stress Index. Choose the
> parameters for hotspot detection.
>
> Processing Section: The system will do the following after you click
> the Run Analysis button:
>
> 1\. Clean up and combine several datasets 2. Prepare spatial data
>
> 3\. Determine each region's Farmer Stress Index.
>
> 4\. Divide areas into three stress categories: low, medium, and high.
> 5. Identify hotspots in space
>
> 6\. Determine the main causes of stress
>
> Section on Output and Visualization: Geospatial hotspot maps that are
> interactive Stress index tables broken down by region Charts
> displaying the contributions of indicators An analytical summary
> report that can be downloaded
>
> **4.** **Setting** **Up** **a** **GitHub** **Repository**
>
> [<u>https://github.com/srlkeerthi593-crypto/Geospatial-farmer-stress-detection/</u>](https://github.com/srlkeerthi593-crypto/Geospatial-farmer-stress-detection/)
> is the repository URL.
>
> The initial folder structure is as follows: /src → source code and
> scripts for spatial analysis; /data → raw and processed datasets; and
> /docs → proposals, reports, and diagrams.
>
> **5.** **Preliminary** **Task** **Distribution**

||
||
||
||
||
||
||

> **Expected** **Outcomes**
>
> Anticipated Results Values of the Farmer Stress Index by region
>
> Finding high-stress farming areas
>
> Maps for the detection of spatial hotspots
>
> An interactive dashboard for geography
>
> Understanding the main reasons why farmers experience stress
