# Image Description for Accessibility Pilot Project

> [!NOTE]  
> This is a fork of the code created by Matt Bollinger during his 2023 internship with the Data Science Lab. Matt's code repo can be found at https://github.com/mlybollinger/accessibility-image-description.

In this project, we apply the capabilities of recent deep learning models to improve image accessibility on Smithsonian websites. State-of-the-art image-text models like BLIP-2 have proven remarkably successful at generating accurate descriptions of images. We seek to make use of those models by building a workflow that scrapes the images, generates alternative text descriptions, and then presents them for human approval.

image_download.py uses a sitemap to scrape the image tags from a provided website. In BLIP_2_testing.py, which we ran on Google Colab, we preprocess and feed each image into the BLIP_2 model to generate a description. Then we feed the images and descriptions into the interface defined in streamlit_app.py to present them for editing and approval.
