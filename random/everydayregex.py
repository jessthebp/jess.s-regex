import re


# ..(\d+).(\d{3}).+
x = re.search('..(\d+).(\d{3}).+', txt)

# matches:
#718-555-3810
#9175552849
#1 212 555 3821
#(917)5551298
#212.555.8731

#does not match
# aslkdjf;as
# sjdf

#why is it written this way?
# .. - match anything to start. this allows for +1, 1 , or (1
#(\d+) - include a string of numbers
# include at least one string of 3 numbers in a row
# allow for trailing anything - this allows for the last few to be a number or text (707-GET-YOURS etc) 
# could also be ..(\d+).(\d{3}).(\d+|\D+)
# you could also use
#..(\d+).(\d{3}).(\d{4}|\D{4})
# but that misses out on some configurations
