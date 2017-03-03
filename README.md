# RemD
Experimenting with the RemD Model.


TODOs
=====

  Selection for Country: Currently presence/absemce. Need to make this a scoring factor.
  
  Does not yet take account of Pest status - "Minor" or "Major"
  
  Weather data is only precipitation at present - no account of wind or temperature
  
  Naming of methods is a bit clumsy - need to ridy this up.
  
  Have written code to access Soil data is from SoilGrids but soil information is not used at present
  
  Creation of a two column List in e.g. creating a List of pests for crop shouldn't work but seems to. Need to understand this. (It should probably be a Dict, as in the applyModelFactors function.)
  
Other Notes
===========

The model data spreadsheet had inconsistent headings (e.g. "Scientific name", "Scientific Name", "Scientific" ...
When used to identify columns in a DataFrame these differences matter so the spreadsheet was fixed, in my copy only.

The number of pest species for which we have have model scores is small compared to the number listed for each country/crop
E.g. for Maize in Kenya, we have 855 spp in keya, and 865 for Maize but in the table of model values there are only 29 records for Maize,  - so we can only operate on those 29. Once filtered for country/crop we end up with 11 spp for which we have model factors.

Thresholds for "wet", "Dry" etc. are arbitrary.
Ideally we will compare recent weather with mean data for the location. The lattter is available but for a fee (with a short free trial.)


TODOs - Done
============

xxx
