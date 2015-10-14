#!/usr/bin/env python

# Links and info about metacontainers.
# Update this file to update the containers.

# Size is in MB

#return dictionary of strings and integers
def get():
          containers = {} 

          #date updated
          containers['date'] = 'May 2013'
          
          containers['url_tuxen'] = 'http://user.gosub.dk/eldorado/'
          containers['url_mega'] = 'http://mega.co.nz/'
          containers['url_firedrive'] = 'http://firedrive.com/'
          
          #--- Database Meta Container ---# 
          containers['db_filename'] = 'video_cache.zip'
          containers['db_size'] = 2
                    
          #--- Movie Meta Container ---# 

          #basic container        
          containers['mv_covers_filename'] = 'movie_covers.zip'
          containers['mv_cover_size'] = 89
          
          containers['mv_backdrop_filename'] = 'movie_backdrops.zip'
          containers['mv_backdrop_size'] = 1100
          
          #--- TV   Meta  Container ---#

          #basic container       
          containers['tv_covers_filename'] = 'tv_covers.zip'
          containers['tv_cover_size'] = 223

          containers['tv_banners_filename'] = 'tv_banners.zip'
          containers['tv_banners_size'] = 94

          containers['tv_backdrop_filename'] = 'tv_backdrops.zip'
          containers['tv_backdrop_size'] = 395
          
          
          #additional container
          containers['tv_add_url'] = ''
          containers['tv_add_size'] = 0       


          return containers
