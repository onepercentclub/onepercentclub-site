this.BlueMap = function(elementId, project){
    
    this.el = document.getElementById(elementId);
    
    this.projectApiUrl = '/projects/api/project/';
    
    this.CUSTOM_MAP_STYLE = '1pct';
    
    // Our favorite settings for Google Maps
    this.cfg = {
        mapTypeId: google.maps.MapTypeId.ROADMAP,            
        zoom: 7, 
        mapTypeControl: true,
        zoomControl: true,
        panControl: false,
        scaleControl: true,    
        streetViewControl: false,
        zoomControlOptions: {
            style: google.maps.ZoomControlStyle.SMALL
        },
        mapTypeControlOptions: {
        mapTypeIds: [
                    google.maps.MapTypeId.ROADMAP, 
                    google.maps.MapTypeId.TERRAIN, 
                    google.maps.MapTypeId.SATELLITE, 
                    google.maps.MapTypeId.HYBRID,
                    this.CUSTOM_MAP_STYLE,
                ]
        },
        overviewMapControl: true,
    };
    
    if (undefined != project) {
        var my = this;
        this.project = project;
        my.cfg.center =  new google.maps.LatLng(project.latitude, project.longitude);
    };
    
    
    this.projectFilters = 'limit=1000';
    
    // To store and clear markers
    this.markers = [];

    this.mapStyle = [
      {
        featureType: "administrative.country",
        elementType: "geometry",
        stylers: [
          { color: "#FFFFFF" },
          { weight: 1 },
          { lightness: 1 },
        ]
      },{
        elementType: "labels.text.stroke",
        stylers: [
          { color: "#FFFFFF" },
          { weight: 2 },
          { lightness: 1 }
        ]
      },{
        elementType: "labels.text.fill",
        stylers: [
          { color: "#000000" },
          { weight: 1 },
          { lightness: 1 },
        ]
      },{
        featureType: "road",
        elementType: "geometry",
        stylers: [
          { color: "#333333" },
          { lightness: 30 }
        ]
      },{
        featureType: "poi",
        elementType: "geometry.fill",
        stylers: [
          { color: "#00C051" }
        ]
      },{
        featureType: "landscape",
        elementType: "geometry.fill",
        stylers: [
          { color: "#00C051" }
        ]
      },{
        featureType: "water",
        stylers: [
          { color: "#FEAAC7" },
          { color: "#99EEBB" },
        ]
      },{
      }
    ];

    this.icons = {
        green: new google.maps.MarkerImage('/static/assets/global/images/icons/1pct_pointer_green.png',
          new google.maps.Size(30, 30),
          new google.maps.Point(0,0),
          new google.maps.Point(7, 32)),
        pink: new google.maps.MarkerImage('/static/assets/global/images/icons/1pct_pointer_pink.png',
          new google.maps.Size(30, 30),
          new google.maps.Point(0,0),
          new google.maps.Point(7, 32)),
        shadow: new google.maps.MarkerImage('/static/assets/global/images/icons/1pct_pointer_shadow.png',
          new google.maps.Size(55, 30),
          new google.maps.Point(0,0),
          new google.maps.Point(7, 30))
    };


    this.getMap = function(cfg) {
        var my = this;        
        if (undefined == my.map) {
            for (i in cfg) {
                my.cfg[i] = cfg[i];
            };
            my.map = new google.maps.Map(my.el, my.cfg);
            
            // Add our custom MapStyle
            my.addMapStyle('1pct', my.mapStyle, '1%COLORS');

        };
        return my.map;
    };

    
    this.addMapStyle = function(name, styles, title) {
        var my = this;
        if (undefined == title) {
            title = name;
        };
          
          var MyMapType = new google.maps.StyledMapType(styles, {name: title});

        my.map.mapTypes.set(my.CUSTOM_MAP_STYLE, MyMapType);            
        my.map.setMapTypeId(my.CUSTOM_MAP_STYLE);        
    };
    
    /**
     * Load projects for the current viewport
     * Extra filters can be given through 'filters' 
     * filters as objects {title_startswith: 'a'} 
     */
    this.loadProjects = function(filters) {

        if (undefined != filters) {
            this.projectFilters = filters;
        };
        var my = this;

        var coords = my.map.getBounds();
        var url = my.projectApiUrl;
        url += '?latitude__gte=' + coords.getSouthWest().lat(); 
        url += '&latitude__lte=' + coords.getNorthEast().lat(); 
        url += '&longitude__gte=' + coords.getSouthWest().lng(); 
        url += '&longitude__lte=' + coords.getNorthEast().lng(); 
        url += '&' + this.projectFilters;

        $('#maploading').show();
        $.getJSON(url, function(data){
            for (m in my.markers) {
                my.markers[m].setMap(null);
            };
            $('#maploading').hide();
            var projects = data.objects;
            for (i in projects) {
                var pos = new google.maps.LatLng(projects[i].latitude, projects[i].longitude);
                if (projects[i].slug == my.project.slug) {
                     var marker = new google.maps.Marker({
                             position: pos,
                            map: my.map,
                            icon: my.icons.pink,
                            shadow: my.icons.shadow
                        });
                } else {
                     var marker = new google.maps.Marker({
                             position: pos,
                            map: my.map,
                            icon: my.icons.green,
                            shadow: my.icons.shadow
                        });
                };
                my.markers.push(marker);
            };
        });
        
    };

    this.showProjects = function(filter) {
        var my = this;
        // Listen to map changes to load projects
        // Wait until map is dawn drawing
        // and then get all projects that are on this map...  
        google.maps.event.addListener(my.map, 'idle', function() {
            my.loadProjects(filter);
        });
        return my;
    };
    
    // Get it going!
    this.map = this.getMap();
    return this;
    
};
