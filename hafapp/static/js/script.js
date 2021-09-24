	$(document).ready(function(){
		$('#delete_btn').click(function(){
			if(confirm("Are you sure?")){
				var id=$('#friend_list :selected').val()
			}
			$.ajax({
				url:"/removefriend/"+ id,
				method: "Get",
				
				success:function(response){
					$('#friend_list :selected').remove()
				}
			})
		});
	});

	$(document).ready(function(){
		$('#splitbill').click(function(){
			
			var fooditems = prompt("Please enter the number of items on receipt")
			
			if(fooditems != null){
				$('#splitbill').attr("href","/ordersetup2/"+ fooditems)
				
			}
		});
	});
	
	// $(document).ready(function(){
	// 	$('#clickdiv').click(function(){
			
	// 		if($('#preview').css('display', 'none')){
	// 			alert("True")
	// 		}
	// 		else{
	// 			alert("False")
	// 		}
	// 	})
	// })

	// $(document).ready(function(){
	// 	$('div.clickdiv').on("click", function(){
			
	// 		if($('#preview').css('visibility', 'hidden')){
	// 			$('#preview').css('visibility', 'visible')
	// 			alert("True")
	// 		}
	// 		else{
	// 			// $('#preview').css('visibility', 'hidden')
	// 			alert("false")
	// 		}
	// 	})

	// })