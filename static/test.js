$.ajax( { url: "https://api.mlab.com/api/1/databases/c4e6db/collections/users/"+ {{ pet._id }} + ""+ "apiKey=qPzoH9RcOcSirKhmznNMhN1Tgv2Y7BlL",
		  data: JSON.stringify( { "$set" : { "vote" : clicks } } ),
		  type: "PUT",
		  contentType: "application/json" } );/**
 * Created by admin on 10/24/2016.
 */
