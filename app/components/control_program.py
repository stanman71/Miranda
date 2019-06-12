


""" ################# """
""" program functions """
""" ################# """


def LED_START_PROGRAM_THREAD(group_id, program_id):

    try:
        LED_TURN_OFF_GROUP(group_id)
        
        # set current state
        program_name = GET_LED_PROGRAM_BY_ID(program_id).name  
        
        
        content = GET_LED_PROGRAM_BY_ID(program_id).content

        for line in content.splitlines():
            
            if "rgb" in line or "color_temp" in line: 
                brightness = line.split(":")[2]
                break
        
        SET_LED_GROUP_CURRENT_SETTING(group_id, program_name)
        SET_LED_GROUP_CURRENT_BRIGHTNESS(group_id, int(brightness))

        # start thread
        Thread = threading.Thread(target=LED_PROGRAM_THREAD, args=(group_id, program_id, ))
        Thread.start()  
        
        return "" 
     
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "LED | start program | " + str(e))
        return str(e)
    

def LED_PROGRAM_THREAD(group_id, program_id):

    if GET_GLOBAL_SETTING_VALUE("zigbee2mqtt") == "True":
        
        content = GET_LED_PROGRAM_BY_ID(program_id).content

        # select each command line
        for line in content.splitlines():

            if "led_rgb" in line: 
                led_id = line.split(":")[0]
                
                if led_id == "1":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_1
                if led_id == "2":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_2                    
                if led_id == "3":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_3                  
                if led_id == "4":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_4  
                if led_id == "5":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_5  
                if led_id == "6":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_6                    
                if led_id == "7":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_7                  
                if led_id == "8":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_8  
                if led_id == "9":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_9  

                rgb        = re.findall(r'\d+', line.split(":")[1])
                red        = rgb[0]
                green      = rgb[1]           
                blue       = rgb[2]
                
                brightness = line.split(":")[2]
                
                SETTING_LED_RGB(led_name, int(red), int(green), int(blue), int(brightness))

            if "led_white" in line: 
                led_id = line.split(":")[0]

                if led_id == "1":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_1
                if led_id == "2":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_2                    
                if led_id == "3":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_3                  
                if led_id == "4":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_4  
                if led_id == "5":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_5  
                if led_id == "6":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_6                    
                if led_id == "7":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_7                  
                if led_id == "8":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_8  
                if led_id == "9":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_9   

                color_temp = re.findall(r'\d+', line.split(":")[1])
                color_temp = color_temp[0]
                
                brightness = line.split(":")[2]
                
                SETTING_LED_WHITE(led_name, int(color_temp), int(brightness))

            if "led_simple" in line: 
                led_id = line.split(":")[0]

                if led_id == "1":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_1
                if led_id == "2":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_2                    
                if led_id == "3":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_3                  
                if led_id == "4":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_4  
                if led_id == "5":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_5  
                if led_id == "6":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_6                    
                if led_id == "7":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_7                  
                if led_id == "8":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_8  
                if led_id == "9":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_9   

                brightness = line.split(":")[1]
                
                SETTING_LED_SIMPLE(led_name, int(brightness))

            if "pause" in line: 
                break_value = line.split(":")
                break_value = int(break_value[1])
                time.sleep(break_value)
                
        time.sleep(1)
        
        return LED_CHECK_SETTING() 
              
    else:
        return ["Keine LED-Steuerung aktiviert"]   
