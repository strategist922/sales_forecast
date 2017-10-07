# Sales Forecast by Product

In the business world, sales forecasting is crucial. With good modeling and prediction, inventory cost is reduced and operation efficiency is improved.

## Background

### The Company

This piece of code attempts to apply ARIMA model in sales prediction on a product-by-product basis. It has been used in a small medical device company based in American Midwest. The company has factory in China and the lead time is typically 1 - 2 months. If a product is out of stock, the company orders air shipment from China, which is expensive.

### Products

The products mainly include drug testing kits. Each product is a unique combination of drug testing strips that can test up to 16 different drugs. And there are over 100 different products. Some products have maintained three years of records. However, a small portion of products are newly marketed and have very short sales history (typically since 2016).

In this publication, product codes are omitted for confidentiality.


### The Model
The available data include sales quantities of each product from Jan 2014 through May 2017. The last 5 months of records are reserved for model testing. Also, the data are pulled from QuickBooks Enterprise 2016, with time ("yyyy-mm") on column and product on row, which needs a transpose upon initiation.

![Data Snapshot](data/data_snapshot.png 'Data Snapshot')
**

After some exploratory data analyses (EDA), ARIMA is selected. It is the ideal algorithm for time series modeling and predicting. A simple stationarity check rules out new products because they typically have high order of difference. This portion of products are submitted for human determination.

An example of current product:

![Current Products](eda_fig/demo_cur.png 'Current Products Maintain Good Records')

An example of new product, notice its short history:
![New Products](eda_fig/demo_new.png 'Newly Marketed Products')

After successfully fitted on the 36-month sales data, the model is tested using the sales data generated in the first 5 months of 2017. And finally, the model is used to predict sales for each existing (as opposed to new) products for the next 6 months and on a rolling basis (with modifications).

![Projection](result/demo.png 'A Projection with Mixing History and Prediction')

## Prerequisites

### Software

* macOS Sierra
* Python 3.6.2
* IPython 5.3.0
* Modules including:
  - os
  - datetime
  - numpy
  - pandas
  - matplotlib
  - statsmodels
  - sqlalchemy

### Running

1. Navigate to the project folder and start Terminal from the folder. Otherwise, use ```cd``` command to navigate here.

2. Copy and paste code chunks as needed. Be sure to modify according to specific environment and tasks.

3. Limbos are stored under corresponding folders.

## Limitations

### Too few records

In practice, 3 years of records strike a balance between too few observations and too few available products. If we chose, say 10 years of records, most products will be ruled out as "new" products and subject to human determination. However, in the age of big data, 36 months still seem too short.

But what if we pulled data in the period of week? That amounts to 52 * 3 = 156 weeks of records. The problem is that sales are not as smooth as those of online retailers for a B2B business. It makes no sense dissecting sales history into weeks.

### Incomplete automation with new products determined manually

In the future, the business will create complicated models that deal with products with short history. But for now, some hunch of and insight into the market make human irreplaceable. In the movie *Star Trek IV: The Voyage Home*, Captain Kirk asks Mr Spock to guess a parameter for their return to the future, which is a torture for Mr Spock, who is the embodiment of pure logic.

### Sales prediction vs. production plan

This prediction or forecasting is in any sense only a draft for how many of each product will be ordered in the future. Taking into consideration of lead time and shipping costs, the result of this piece of code is hardly the final version of production plan. Some specialized models should also be considered. For example, EOQ model accounts for holding costs and other factors, which is ideal in determining the timetable for production, from procurement of raw materials to hiring production workers and so on. Also, predictions of product sales must be decomposed to individual drug tested. In essence, the company manufactures test strips, not plastic containers.

## Updates

* 10/06/2017 Initial release after confidentiality check.

## License
 GPL3
