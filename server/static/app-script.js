angular.module('App', [])
	.controller('homeController', function($scope) {
		$scope.results = {
			results: [
			{
			title: "Apple - iPhone 4S - The most amazing iPhone yet.",
			kwic: "The faster dual-core A5 chip. The 8MP camera with all-new optics also shoots 1080p HD video. And introducing Siri. It's the most amazing iPhone ...",
			content: "",
			url: "http://www.apple.com/iphone/",
			iurl: "http://images.apple.com/iphone/home/images/video4-ad.png",
			domain: "www.apple.com",
			author: "",
			news: false,
			votes: "1",
			date: 1328182356634,
			related: [ ]
			},
			{
			title: "iPhone - Wikipedia, the free encyclopedia",
			kwic: "and released on June 29, 2007. The 5th generation iPhone, the iPhone 4S , was announced on October 4, 2011, and released 10 days later. An iPhone ...",
			content: "",
			url: "http://en.wikipedia.org/wiki/Iphone",
			iurl: "http://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/IPhone_4S_No_shadow.png/220px-IPhone_4S_No_shadow.png",
			domain: "en.wikipedia.org",
			author: "",
			news: false,
			votes: "1",
			date: 1328182357954,
			related: [ ]
			},
			{
			title: "A Closer Look At The iPhone",
			kwic: "Apple Inc's Phil Schiller shows John Blackstone the many features of the iPhone. Apple's latest product will go on sale this June.",
			content: "",
			url: "http://www.youtube.com/watch?v=YgW7or1TuFk",
			iurl: "http://i.ytimg.com/vi/YgW7or1TuFk/default.jpg",
			domain: "www.youtube.com",
			author: "",
			news: false,
			votes: "1",
			date: 1328182424399,
			related: [ ]
			},
			{
			title: "iPhone - Wikipedia, the free encyclopedia",
			kwic: "... 5S , 6 , and 6 Plus Bluetooth 4.0 The user interface is built around the device's multi-touch screen, including a virtual keyboard . The iPhone ...",
			content: "",
			url: "http://en.wikipedia.org/wiki/Apple_iPhone",
			iurl: "http://upload.wikimedia.org/wikipedia/en/thumb/0/01/IPhone6_silver_frontface.png/150px-IPhone6_silver_frontface.png",
			domain: "en.wikipedia.org",
			author: "",
			news: false,
			votes: "1",
			date: 1412796657879,
			related: [ ]
			},
			{
			title: "iPhone Murder Apps2010 - Imdb",
			kwic: "Directed by Lauren Palmigiano. With Emma Stone.",
			content: "",
			url: "http://www.imdb.com/title/tt1741714/",
			iurl: "http://i.media-imdb.com/images/SFc0774313bf9ccbfe22050c8bb4029e41/imdb-share-logo.gif",
			domain: "www.imdb.com",
			author: "",
			news: false,
			votes: "1",
			date: 1328182424461,
			related: [ ]
			},
			{
			title: "Find My iPhone - iTunes",
			kwic: "If you misplace your iPhone, iPad, iPod touch, or Mac, the Find My iPhone app will let you use another iOS device to find it and protect your ...",
			content: "",
			url: "http://itunes.apple.com/us/app/find-my-iphone/id376101648?mt=8&uo=4",
			iurl: "http://a5.mzstatic.com/us/r1000/070/Purple/09/cb/6e/mzl.duxhsjuk.png",
			domain: "itunes.apple.com",
			author: "",
			news: false,
			votes: "1",
			date: 1328182424555,
			related: [ ]
			},
			{
			title: "iPhone - CrunchBase",
			kwic: "Apple 's iPhone was introduced at MacWorld in January 2007 and officially went on sale June 29, 2007, selling 146,000 units within the first ...",
			content: "",
			url: "http://www.crunchbase.com/product/iphone",
			iurl: "http://www.crunchbase.com/assets/images/resized/0001/9797/19797v1-max-450x450.jpg",
			domain: "www.crunchbase.com",
			author: "",
			news: false,
			votes: "1",
			date: 1328182425102,
			related: [ ]
			},
			{
			title: "How-to articles for iPhone development and Objective-C",
			kwic: "This question is protected to prevent thanks!, me too!, or spam answers by new users. To answer it, you must have earned at least 10 reputation ...",
			content: "",
			url: "http://stackoverflow.com/questions/1939/timeline",
			iurl: "",
			domain: "stackoverflow.com",
			author: "",
			news: false,
			votes: "1",
			date: 1328182425748,
			related: [ ]
			},
			{
			title: "Apple iPhone 3G 8GB - Unlocked - Amazon",
			kwic: "The Apple iphone 3G 8GB - Unlocked is the second generation Apple device designed to work anywhere in the world. Just pop in your sim card and ...",
			content: "",
			url: "http://www.amazon.com/Apple-iPhone-3G-8GB-Unlocked/dp/B001UBB9GM%3FSubscriptionId%3DAKIAJRYMXCDEOMTT56BQ%26tag%3Dwwwfaroocom-20%26linkCode%3Dxm2%26camp%3D2025%26creative%3D165953%26creativeASIN%3DB001UBB9GM",
			iurl: "http://ecx.images-amazon.com/images/I/31tyhGdzX9L.jpg",
			domain: "www.amazon.com",
			author: "",
			news: false,
			votes: "1",
			date: 1328182426596,
			related: [ ]
			},
			{
			title: "Next iPhone News, Latests Rumors",
			kwic: "News, Rumors and Tips about the Apple iPhone 5S, IPhone 5C, and IPhone 6",
			content: "",
			url: "http://www.nextiphonenews.com/",
			iurl: "http://www.nextiphonenews.com/wp-content/uploads/2013/10/NIN_logo_1_modified_220x76.jpg",
			domain: "www.nextiphonenews.com",
			author: "",
			news: false,
			votes: "1",
			date: 1387863671552,
			related: [ ]
			}
			],
			query: "iphone",
			suggestions: [ ],
			count: 100,
			start: 1,
			length: 10,
			time: "16"
		};
		$scope.summary="Here goes the summary"
		$scope.processQuery = function() {
			console.log($scope.query)
			$scope.query = '';
		};
	});