# Common Questions

Here are some answers to the questions we get most often.

## Data input

**What kind of computer do I need to run this?**

The tool will run on any computer that can run Python. There are some extra performance capabilities if you have an
Nvidia CUDA-compatible GPU that will make things run faster, but it's not required.

**What resolution should my data be?**

Kelp-O-Matic was designed to work best on imagery with 1cm to 10cm pixel resolution. 5cm resolution is likely optimal.
For the PlanetScope model, the input resolution should be 3m or better and use the surface reflectance bands.

**When I run the tool, it starts giving me warnings. Should I worry?**

The warnings are there to give you optional suggestions or hints about things that might be non-optimal. You don't need
to worry about them, but by reading them and making the suggested adjustments, you may find processing to proceed more
quickly.

**Will Kelp-O-Matic work for my data, which is not from western North America?**

While Kelp-O-Matic was trained primarily on data from British Columbia and California, it has shown good performance in
other regions like Alaska and Patagonia. The model may work best with imagery similar to our training data, but we
actively work to improve its performance across different geographical areas. If you find the model isn't performing
well with your data, please contact us - we're interested in expanding the model's capabilities and may be able to
optimize it for your specific region.

**Will Kelp-O-Matic work better on my images if I pass in sensor band X for instead of e.g. the red band?**

Most likely no, this won't work. The model is specifically trained to use the relationships between the RGB (and NIR,
for certain models) bands to determine if kelp/mussels are present.

## Model output

**The output image is all black. I think it didn't find anything!**

The model outputs images with pixel values in the range of 0 to 3, depending on which model was
used ([see here](about.md#model-outputs) for a summary). Make sure that you visualize the outputs in your GIS by 
"unique values" to see the output.

**When I open my outputs in a GIS they are not in the same place as the ortho!**

Check that your orthomosaic has an assigned geographic coordinate system and try again. You can do this in various GIS
software.

---

*Still have a question?*

Get in touch by [sending us an email](mailto:kom.support@hakai.org)
or [file a GitHub issue](https://github.com/HakaiInstitute/kelp-o-matic/issues)
