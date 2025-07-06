# Commission Autosorter

[中文Readme](Readme.cn.md)

This project works together with [ALAS](https://github.com/LmeSzinc/AzurLaneAutoScript).
ALAS tells you what commission rewards you got, but thousands of commissions can be annoying.
I wrote this to make the sorting process (which probably no one other than me does)
easier.

## Usage
### Data Analyzing
1. Put your images in whatever folder you want, main.py will ask you anyways. The default folder is `commission` since that's where alas puts all the images.
2. Run `main.py`.
    - Make sure you have enough space in you drive! `main.py` _**COPIES**_ all the images to the input folder, so there will be a temporary usage of your disk.
3. <del>Check out the [instructions](https://github.com/LmeSzinc/AzurLaneAutoScript/wiki/item_statistics_en) to using the official stats tool provided by ALAS.</del><br>Just copy `tools/item_statistics.py` to your `AzurLaneAutoScript` folder. Then use `./toolkit/python item_statistics.py` to run it.
    - **Important**: To make the temporary templates correct you have to change `module\statistics\get_items.py` temporarily. Change the last lines to 
    ```
    im_bgr = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
    cv2.imwrite(os.path.join(folder, f'{name}.png'), im_bgr)
    ```
     and change back after you are done. Else you will see strange BGR colors in the output images.
    - If you use default settings in this repo the folder of your `FOLDER` in that script will be `./Result`.
    - You don't need to do the first run, since we'll cover that with `data_proc.py`. BTW, my assets should be more robust than the official ones.
    - Even though the first run is not mandatory, I still hope you will run it, <span style="color:red">since the assets that pop up in your folder can make this repo stronger.</span> I won't bother to submit it to ALAS though cause that's a scary thing to do QWQ.
    - If you see sth like `Warning: not drop_image` it's fine since ALAS sometimes screenshots the main page due to clicking too quickly, or simply because nothing was dropped. This issue causes minimal error in the final result since sometimes something is droped but not screenshot.
4. Run `data_proc.py`. It will guide you to fill out the assets that were not recognized by ALAS.
5. Enjoy your statistics. You can boast about it now!

### Notes
You might notice that ALAS assets are strange in color. That's because LME made a mistake when using cv2, use `rotate_channels()` in `tools.py` to correct that color issue.


### Seperate Scripts
Every script can also run on itself, you can run them directly or build your own processing chain. There are some pre-defined utilities in `tools.py` that you might find useful while doing filesystem operations.

Put stuff in TODO folder (**Read the config.yaml to see which subfolder you should put it in**) and run the script that has your desired effect. Check the results in the folder that pops up.

I will see if I can write `requirements.txt`, but that's when I happen to have the time.

## What's here

Alas stacks up all the commissions it checks at one time, which is kind of annoying.
So I wrote a script to divide them into separate stacks.

Also ALAS does not check if the commission is a major success, so I added that as well.

Here's what else I want to do:
- Add a way to check which sort of commission it is by checking the reward image
- Remove the main page image that ALAS sometimes mistakenly puts into the screenshot

