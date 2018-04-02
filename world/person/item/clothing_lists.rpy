##Standard standing images taken at 1920x420 regardless of item size, so they can be tiled.

init -1:     
    define mannequin_average = Image("mannequin_average.png") #Define the mannequin image we use for preview in all of the option selects.
    
    ## COLOUR DEFINES ##
    # Here we define colours as a 0 to 1 float for red, green, blue, and alpha. 0,0,0,1 would corriospond to perfect black everywhere, 1,1,1,1 corrisponds to no modification to the original greyscale.
    
    define colour_black = [0.1,0.1,0.1,1] #A soft, natural fabric black.
    define colour_red = [0.6,0.1,0.1,1]
    define colour_green = [0.2,0.4,0.2,1]
    define colour_sky_blue = [0.4,0.6,0.9,1]
    define colour_dark_blue = [0.15,0.20,0.80,1]
    define colour_yellow = [0.9,0.8,0.05,1]
    define colour_pink = [1.0,0.8,0.85,1]
    
    define colour_black_sheer = [0.1,0.1,0.1,0.96] #Makes use of the alpha channel to give us translucent material that very slightly shows what's underneath.
    

##NOTE/REMINDER##
#Stand1 positions are taken as 420x1080 images with 800 offset
#Stand2 positions are taken as 500x1080 images with 800 offset
#Stand3 positions are taken as 500x1080 images with 750 offset

#Doggy positions are taken as 700x1080 images with 600 offset
    
    python:
        
        ##CLOTHING##
        
        ##Panties
        panties_list = []
        pink_panties = Clothing("pink panties", 1, True, True, "Pink_Panties", ["stand1","stand2","stand3","doggy"], False, True, 0, colour = colour_pink) ##Made white by desaturating (lightness), then bright/contrast (110, 75)
        panties_list.append(pink_panties)
        
        black_panties = Clothing("black panties", 1, True, True, "Pink_Panties", ["stand1","stand2","stand3","doggy"], False, True, 0, colour = colour_black)
        panties_list.append(black_panties)
        
        red_panties = Clothing("red panties", 1, True, True, "Pink_Panties", ["stand1","stand2","stand3","doggy"], False, True, 0, colour = colour_red)
        panties_list.append(red_panties)
        
        thin_red_panties = Clothing("thin red panties", 1, True, True, "Red_Panties", ["stand1","stand2","stand3","doggy"], False, True, 1, colour = colour_red) ##Made white by desaturating (lightness), then bright/contra (120,90)
        panties_list.append(thin_red_panties)
        
        thin_black_panties = Clothing("thin black panties", 1, True, True, "Red_Panties", ["stand1","stand2","stand3","doggy"], False, True, 2, colour = colour_black_sheer)
        panties_list.append(thin_black_panties)
        
        thin_pink_panties = Clothing("thin pink panties", 1, True, True, "Red_Panties", ["stand1","stand2","stand3","doggy"], False, True, 1, colour = colour_pink)
        panties_list.append(thin_pink_panties)
        
        black_thong = Clothing("black thong", 1, True, True, "Black_Thong", ["stand1","stand2","stand3","doggy"], False, True, 4, colour = colour_black) ##Made white by using standard gimp invert. TODO: rerender to true white
        panties_list.append(black_thong)
        
        pink_thong = Clothing("pink thong", 1, True, True, "Black_Thong", ["stand1","stand2","stand3","doggy"], False, True, 4, colour = colour_pink)
        panties_list.append(pink_thong)
        
        red_thong = Clothing("red thong", 1, True, True, "Black_Thong", ["stand1","stand2","stand3","doggy"], False, True, 4, colour = colour_red)
        panties_list.append(red_thong)
        
        lace_panties = Clothing("black lace panties", 1, True, True, "Lace_Panties", ["stand1","stand2","stand3","doggy"], False, True, 2, colour = colour_black) ##Made white by using standard gimp invert. TODO: rerender to true white
        panties_list.append(lace_panties)
        
        pink_lace_panties = Clothing("pink lace panties", 1, True, True, "Lace_Panties", ["stand1","stand2","stand3","doggy"], False, True, 2, colour = colour_pink)
        panties_list.append(pink_lace_panties)
        
        red_lace_panties = Clothing("red lace panties", 1, True, True, "Lace_Panties", ["stand1","stand2","stand3","doggy"], False, True, 2, colour = colour_red)
        panties_list.append(red_lace_panties)
        
        ##Bras
        bra_list = []
        
        pink_bra = Clothing("pink bra", 1, True, True, "Pink_Bra", ["stand1","stand2","stand3","doggy"],True, True, 0, colour = colour_pink) #Recoloured white with desat, bright/contra 15/40
        bra_list.append(pink_bra)
        
        red_bra = Clothing("red bra", 1, True, True, "Pink_Bra", ["stand1","stand2","stand3","doggy"],True, True, 0, colour = colour_red)
        bra_list.append(red_bra)
        
        black_bra = Clothing("black bra", 1, True, True, "Pink_Bra", ["stand1","stand2","stand3","doggy"],True, True, 0, colour = colour_black)
        bra_list.append(black_bra)
        
        small_red_bra = Clothing("small red bra", 1, True, True, "Red_Bra", ["stand1","stand2","stand3","doggy"],True, True, 2, colour = colour_red) #Recoloured with desat, bright/contra 125/60
        bra_list.append(small_red_bra)
        
        small_pink_bra = Clothing("small pink bra", 1, True, True, "Red_Bra", ["stand1","stand2","stand3","doggy"],True, True, 2, colour = colour_pink)
        bra_list.append(small_pink_bra)
        
        small_black_bra = Clothing("small black bra", 1, True, True, "Red_Bra", ["stand1","stand2","stand3","doggy"],True, True, 2, colour = colour_black)
        bra_list.append(small_black_bra)
        
        black_corset = Clothing("black corset", 1, True, True,"Black_Corset", ["stand1","stand2","stand3","doggy"],True, True, 5)
        bra_list.append(black_corset)
        
        lace_bra = Clothing("lace bra", 1, True, True,"Lace_Bra", ["stand1","stand2","stand3","doggy"],True, True, 2)
        bra_list.append(lace_bra)
        
        ##Pants
        pants_list = []
        
        jeans = Clothing("jeans", 2, True, True, "Long_Jeans", ["stand1","stand2","stand3","doggy"], False, False, 0)
        pants_list.append(jeans)
        
        shorts = Clothing("shorts", 2, True, True, "Shorts", ["stand1","stand2","stand3","doggy"], False, False, 2)
        pants_list.append(shorts)
        
        jean_hotpants = Clothing("jean hotpants", 2, True, True, "Jean_Hotpants", ["stand1","stand2","stand3","doggy"], False, False, 3)
        pants_list.append(jean_hotpants)
        
        pants = Clothing("black pants", 2, True, True, "Black_Pants", ["stand1","stand2","stand3","doggy"], False, False, 0)
        pants_list.append(pants)
        
        suitpants = Clothing("suit pants", 2, True, True, "Suit_Pants", ["stand1","stand2","stand3","doggy"], False, False, 0)
        pants_list.append(suitpants)
        
        leggings = Clothing("leggings", 2, True, True, "Black_Leggings", ["stand1","stand2","stand3","doggy"], False, False, 1)
        pants_list.append(leggings)
        
        blue_minishorts = Clothing("blue minishorts", 2, True, True, "Blue_Minishorts", ["stand1","stand2","stand3","doggy"], False, False, 5)
        pants_list.append(blue_minishorts)
        
        red_minishorts = Clothing("red minishorts", 2, True, True, "Red_Minishorts", ["stand1","stand2","stand3","doggy"], False, False, 5)
        pants_list.append(red_minishorts)
        
        ##Skirts
        skirts_list = []
        
        navy_skirt = Clothing("navy skirt", 2, True, False, "Navy_Skirt", ["stand1","stand2","stand3","doggy"], False, False, 0)
        skirts_list.append(navy_skirt)
        
        red_skirt = Clothing("red skirt", 2, True, False, "Red_Skirt", ["stand1","stand2","stand3","doggy"], False, False, 1)
        skirts_list.append(red_skirt)
        
        short_skirt = Clothing("short skirt", 2, True, False, "Pleated_Skirt", ["stand1","stand2","stand3","doggy"], False, False, 3)
        skirts_list.append(short_skirt)
        
        mini_skirt = Clothing("mini skirt", 2, False, False, "Mini_Skirt", ["stand1","stand2","stand3","doggy"], False, False, 5)
        skirts_list.append(mini_skirt)
        
        ##Dresses
        dress_list = []
        
        sweater_dress_bottom = Clothing("sweater dress", 2, True, False, "Sweater_Dress", [], False, False, 0, is_extension = True)
        sweater_dress = Clothing("sweater dress", 2, True, True, "Sweater_Dress", ["stand1","stand2","stand3","doggy"], True, False, 0, has_extension = sweater_dress_bottom)
        dress_list.append(sweater_dress)
        
        two_part_dress_bottom = Clothing("two part dress", 2, True, False, "Two_Part_Dress", [], False, False, 0, is_extension = True)
        two_part_dress = Clothing("two part dress", 2, True, True, "Two_Part_Dress", ["stand1","stand2","stand3","doggy"], True, False, 3, has_extension = sweater_dress_bottom)
        dress_list.append(two_part_dress)
        
        thin_dress_bottom = Clothing("thin dress", 2, False, False, "Thin_Dress", [], False, False, 0, is_extension = True)
        thin_dress = Clothing("thin dress", 2, False, False, "Thin_Dress", ["stand1","stand2","stand3","doggy"], True, False, 4, has_extension = thin_dress_bottom)
        dress_list.append(thin_dress)
        
        ##Shirts
        shirts_list = []
        
        grey_sweater = Clothing("grey sweater", 2, True, True, "Grey_Sweater", ["stand1","stand2","stand3","doggy"], True, False, 0)
        shirts_list.append(grey_sweater)
        
        purple_sweater = Clothing("purple sweater", 2, True, True, "Purple_Sweater", ["stand1","stand2","stand3","doggy"], True, False, 0)
        shirts_list.append(purple_sweater)
        
        tie_sweater = Clothing("tie sweater", 2, True, True, "Tie_Sweater", ["stand1","stand2","stand3","doggy"], True, False, 0)
        shirts_list.append(tie_sweater)
        
        black_tshirt = Clothing("black tshirt", 2, True, True, "Blue_Tshirt", ["stand1","stand2","stand3","doggy"], True, False, 1, colour = colour_black)
        shirts_list.append(black_tshirt)
        
        dark_blue_tshirt = Clothing("dark blue tshirt", 2, True, True, "Blue_Tshirt", ["stand1","stand2","stand3","doggy"], True, False, 1, colour = colour_dark_blue) #Has been desaturated (lightness) and brightend (115, 55) to turn into greyscale. TODO: change render to simple white.
        shirts_list.append(dark_blue_tshirt)
        
        sky_blue_tshirt = Clothing("sky blue tshirt", 2, True, True, "Blue_Tshirt", ["stand1","stand2","stand3","doggy"], True, False, 1, colour = colour_sky_blue)
        shirts_list.append(sky_blue_tshirt)
        
        red_tshirt = Clothing("red tshirt", 2, True, True, "Blue_Tshirt", ["stand1","stand2","stand3","doggy"], True, False, 1, colour = colour_red)
        shirts_list.append(red_tshirt)
        
        green_tshirt = Clothing("green tshirt", 2, True, True, "Blue_Tshirt", ["stand1","stand2","stand3","doggy"], True, False, 1, colour = colour_green)
        shirts_list.append(green_tshirt)
        
        yellow_tshirt = Clothing("yellow tshirt", 2, True, True, "Blue_Tshirt", ["stand1","stand2","stand3","doggy"], True, False, 1, colour = colour_yellow)
        shirts_list.append(yellow_tshirt)
        
        black_sheer_tshirt = Clothing("sheer black tshirt", 2, True, True, "Blue_Tshirt", ["stand1","stand2","stand3","doggy"], True, False, 6, colour = colour_black_sheer)
        shirts_list.append(black_sheer_tshirt)
        
        long_tshirt = Clothing("long tshirt", 2, True, True, "Long_Tshirt", ["stand1","stand2","stand3","doggy"], True, False, 0)
        shirts_list.append(long_tshirt)
        
        # Coloured Tanktop Varieties #
        tanktop = Clothing("tanktop", 2, True, True, "White_Tanktop", ["stand1","stand2","stand3","doggy"], True, False, 5)
        shirts_list.append(tanktop)
        
        black_tanktop = Clothing("black tanktop", 2, True, True, "White_Tanktop", ["stand1","stand2","stand3","doggy"], True, False, 5, colour = colour_black)
        shirts_list.append(black_tanktop)
        
        red_tanktop = Clothing("red tanktop", 2, True, True, "White_Tanktop", ["stand1","stand2","stand3","doggy"], True, False, 5, colour = colour_red)
        shirts_list.append(red_tanktop)
        
        green_tanktop = Clothing("green tanktop", 2, True, True, "White_Tanktop", ["stand1","stand2","stand3","doggy"], True, False, 5, colour = colour_green)
        shirts_list.append(green_tanktop)
        
        sky_blue_tanktop = Clothing("sky blue tanktop", 2, True, True, "White_Tanktop", ["stand1","stand2","stand3","doggy"], True, False, 5, colour = colour_sky_blue)
        shirts_list.append(sky_blue_tanktop)
        
        dark_blue_tanktop = Clothing("dark blue tanktop", 2, True, True, "White_Tanktop", ["stand1","stand2","stand3","doggy"], True, False, 5, colour = colour_dark_blue)
        shirts_list.append(dark_blue_tanktop)
        
        yellow_tanktop = Clothing("yellow tanktop", 2, True, True, "White_Tanktop", ["stand1","stand2","stand3","doggy"], True, False, 5, colour = colour_yellow)
        shirts_list.append(yellow_tanktop)
        
        black_sheer_tanktop = Clothing("sheer black tanktop", 2, True, True, "White_Tanktop", ["stand1","stand2","stand3","doggy"], True, False, 8, colour = colour_black_sheer)
        shirts_list.append(black_sheer_tanktop)
        
        
        
        mesh_shirt = Clothing("mesh shirt", 2, False, True, "Mesh_Shirt", ["stand1","stand2","stand3","doggy"], True, False, 5)
        shirts_list.append(mesh_shirt)
        
        ##Socks##
        socks_list = []
        
        socks = Clothing("high socks", 1, True, True, "High_Socks", ["stand1","stand2","stand3","doggy"], False, False, 0)
        socks_list.append(socks)
        
        black_thighhighs = Clothing("thigh high stockings", 1, True, True, "Black_Thighhighs", ["stand1","stand2","stand3","doggy"], False, False, 5)
        socks_list.append(black_thighhighs)
        
        red_nylons = Clothing("red nylons", 1, True, True, "Red_Nylons", ["stand1","stand2","stand3","doggy"], False, False, 5)
        socks_list.append(red_nylons)
        
        fishnets = Clothing("black fishnets", 1, True, True, "Black_Fishnets", ["stand1","stand2","stand3","doggy"], False, False, 10)
        socks_list.append(fishnets)
        
        ##Shoes##
        shoes_list = []
        
        boots = Clothing("boots", 2, True, True, "Boots", ["stand1","stand2","stand3","doggy"], False, False, 0)
        shoes_list.append(boots)
        
        sandles = Clothing("sandles", 2, True, True, "Blue_Sandles", ["stand1","stand2","stand3","doggy"], False, False, 0)
        shoes_list.append(sandles)
        
        brown_shoes = Clothing("brown shoes", 2, True, True, "Brown_Shoes", ["stand1","stand2","stand3","doggy"], False, False, 0)
        shoes_list.append(brown_shoes)
        
        sneakers = Clothing("sneakers", 2, True, True, "Sneakers", ["stand1","stand2","stand3","doggy"], False, False, 0)
        shoes_list.append(sneakers)
        
        
        ##OUTFITS##
        
        ##Girls will prune unsuitable outfits from their default wardrobe
        
        default_outfit_1 = Outfit("Default Outfit 1")
        default_outfit_1.add_lower(pink_panties)
        default_outfit_1.add_upper(pink_bra)
        default_outfit_1.add_feet(sandles)
        default_outfit_1.add_lower(shorts)
        default_outfit_1.add_upper(dark_blue_tshirt)
        
        default_outfit_2 = Outfit("Default Outfit 2")
        default_outfit_2.add_lower(pink_panties)
        default_outfit_2.add_upper(pink_bra)
        default_outfit_2.add_feet(sandles)
        default_outfit_2.add_lower(pants)
        default_outfit_2.add_upper(long_tshirt)
        
        default_outfit_3 = Outfit("Default Outfit 3")
        default_outfit_3.add_lower(pink_panties)
        default_outfit_3.add_upper(pink_bra)
        default_outfit_3.add_feet(socks)
        default_outfit_3.add_feet(sneakers)
        default_outfit_3.add_lower(leggings)
        default_outfit_3.add_upper(purple_sweater)
        
        default_outfit_4 = Outfit("Default Outfit 4")
        default_outfit_4.add_lower(pink_panties)
        default_outfit_4.add_upper(pink_bra)
        default_outfit_4.add_feet(sneakers)
        default_outfit_4.add_lower(jeans)
        default_outfit_4.add_upper(purple_sweater)
        
        default_outfit_5 = Outfit("Default Outfit 5")
        default_outfit_5.add_lower(lace_panties)
        default_outfit_5.add_upper(lace_bra)
        default_outfit_5.add_feet(sandles)
        default_outfit_5.add_dress(sweater_dress)
        
        default_outfit_6 = Outfit("Default Outfit 6")
        default_outfit_6.add_lower(red_panties)
        default_outfit_6.add_upper(red_bra)
        default_outfit_6.add_feet(sandles)
        default_outfit_6.add_dress(sweater_dress)
        
        default_outfit_7 = Outfit("Default Outfit 7")
        default_outfit_7.add_lower(red_panties)
        default_outfit_7.add_upper(red_bra)
        default_outfit_7.add_feet(socks)
        default_outfit_7.add_feet(boots)
        default_outfit_7.add_upper(dark_blue_tshirt)
        default_outfit_7.add_lower(short_skirt)
        
        default_outfit_8 = Outfit("Default Outfit 8")
        default_outfit_8.add_lower(lace_panties)
        default_outfit_8.add_upper(lace_bra)
        default_outfit_8.add_feet(red_nylons)
        default_outfit_8.add_feet(boots)
        default_outfit_8.add_upper(purple_sweater)
        default_outfit_8.add_lower(suitpants)
        
        default_outfit_9 = Outfit("Default Outfit 9")
        default_outfit_9.add_upper(pink_bra)
        default_outfit_9.add_lower(pink_panties)
        default_outfit_9.add_feet(sandles)
        default_outfit_9.add_upper(tie_sweater)
        default_outfit_9.add_lower(navy_skirt)
        
        default_outfit_10 = Outfit("Default Outfit 10")
        default_outfit_10.add_upper(black_corset)
        default_outfit_10.add_lower(black_thong)
        default_outfit_10.add_feet(socks)
        default_outfit_10.add_feet(sneakers)
        default_outfit_10.add_upper(long_tshirt)
        default_outfit_10.add_lower(jeans)
        
        default_outfit_11 = Outfit("Default Outfit 11")
        default_outfit_11.add_upper(pink_bra)
        default_outfit_11.add_lower(pink_panties)
        default_outfit_11.add_feet(sandles)
        default_outfit_11.add_upper(tanktop)
        default_outfit_11.add_lower(jean_hotpants)
        
        default_outfit_12 = Outfit("Default Outfit 12")
        default_outfit_12.add_upper(pink_bra)
        default_outfit_12.add_lower(pink_panties)
        default_outfit_12.add_feet(sandles)
        default_outfit_12.add_upper(tanktop)
        default_outfit_12.add_lower(pants)
        
        default_outfit_13 = Outfit("Default Outfit 13")
        default_outfit_13.add_lower(pink_panties)
        default_outfit_13.add_upper(pink_bra)
        default_outfit_13.add_feet(black_thighhighs)
        default_outfit_13.add_feet(brown_shoes)
        default_outfit_13.add_dress(two_part_dress)
        
        default_outfit_14 = Outfit("Default Outfit 14")
        default_outfit_14.add_upper(pink_bra)
        default_outfit_14.add_lower(pink_thong)
        default_outfit_14.add_feet(sandles)
        default_outfit_14.add_upper(dark_blue_tshirt)
        default_outfit_14.add_lower(mini_skirt)
        
        
        
#        plain_outfit = Outfit("Plain Outfit 1")
#        plain_outfit.add_lower(pink_panties)
#        plain_outfit.add_upper(pink_bra)
#        plain_outfit.add_dress(sweater_dress)
#        plain_outfit.add_feet(socks)
#        plain_outfit.add_feet(sneakers)
        
#        plain_outfit2 = Outfit("Plain Outfit 2")
#        plain_outfit2.add_lower(black_thong)
#        plain_outfit2.add_upper(lace_bra)
#        plain_outfit2.add_lower(pants)    
#        plain_outfit2.add_upper(grey_sweater)
#        plain_outfit2.add_feet(sandles)
        
#        sexy_outfit = Outfit("Sexy Outfit 1")
#        sexy_outfit.add_lower(lace_panties)
#        sexy_outfit.add_lower(shorts)
#        sexy_outfit.add_upper(black_corset)
#        sexy_outfit.add_feet(fishnets)
#        sexy_outfit.add_feet(boots)
        
#        sexy_outfit2 = Outfit("Sexy Outfit 2")
#        sexy_outfit2.add_lower(pink_thong)
#        sexy_outfit2.add_lower(shorts)
#        sexy_outfit2.add_upper(tanktop)
#        sexy_outfit2.add_feet(sandles)
        
#        sexy_outfit3 = Outfit("Sexy Outfit 3")
#        sexy_outfit3.add_dress(two_part_dress)
#        sexy_outfit3.add_lower(black_thong)
#        sexy_outfit3.add_feet(black_thighhighs)
#        sexy_outfit3.add_feet(brown_shoes)
        
#        office_outfit = Outfit("Office Outfit 1")
#        office_outfit.add_lower(pink_thong)
#        office_outfit.add_upper(pink_bra)
#        office_outfit.add_lower(pants)
#        office_outfit.add_upper(tanktop)
#        office_outfit.add_feet(socks)
#        office_outfit.add_feet(brown_shoes)
        
#        office_outfit2 = Outfit("Office Outfit 2")
#        office_outfit2.add_lower(lace_panties)
#        office_outfit2.add_upper(lace_bra)
#        office_outfit2.add_dress(thin_dress)
#        office_outfit2.add_feet(black_thighhighs)
#        office_outfit2.add_feet(brown_shoes)
        
        ##WARDROBES##
        
        default_wardrobe = Wardrobe("Default Wardrobe", [default_outfit_1,default_outfit_2,default_outfit_3,default_outfit_4,default_outfit_5,default_outfit_6,
            default_outfit_7,default_outfit_8,default_outfit_9,default_outfit_10,default_outfit_11,default_outfit_12,default_outfit_13,default_outfit_14])
            
