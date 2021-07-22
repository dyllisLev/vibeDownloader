function downloadEventAdd(downloadType){


  if( downloadType == "search"){
    downloadType = "track";
  }
  $("body").off('click', '#btn_download');
  $("body").off('click', '#btn_download_all');
  $("body").off('click', '#btn_play');
  $("body").on('click', '#btn_download', function(e){
    e.preventDefault();
    
    var trackId = $(this).data('trackid');
    $.ajax({
      url: '/' + package_name + '/ajax/'+sub+'/musicDownloadById',
      type: "POST", 
      cache: false,
      data: {"trackId":trackId, "type":"track"},
      dataType: "json",
      success: function (data) {
        // alert("!");
        // if( data.ret == "success" ){
        //   $.notify('<strong>' + data.content.response.result.track.trackTitle + ' 다운로드 완료</strong>', {type: 'success'});
        // }else{
        //   $.notify('<strong>다운로드 실패</strong>', {type: 'danger'});
        // }
      }
    });
  });


  $("body").on('click', '#btn_download_all', function(e){
    e.preventDefault();
    key = $(this).data("top100key");
    
    $.ajax({
      url: '/' + package_name + '/ajax/'+sub+'/allDownload',
      type: "POST", 
      cache: false,
      data: {"artistId":$(this).data("artistid"),"albumId":$(this).data("albumid"), "type":downloadType, "top100Key":key},
      dataType: "json",
      success: function (data) {
        if( data.ret == "success" ){
          $.notify('<strong>다운로드를 시작합니다.</strong>', {type: 'success'});
        }else{
          $.notify('<strong>다운로드 실패</strong>', {type: 'danger'});
        }
      }
    });
    
  
  });

  $("body").on('click', '#btn_play', function(e){
    e.preventDefault();
    var trackId = $(this).data('trackid');
    btnObj = $(this);
    
    if( btnObj.text() == "재생"){
      $.ajax({
        url: '/' + package_name + '/ajax/'+sub+'/musicPlay',
        type: "POST", 
        cache: false,
        data: {"trackId":trackId, "type":"track"},
        dataType: "json",
        success: function (data) {
          if( data.ret == "success" ){
            
            var videoSrc = data.musicUrl; // <- 테스트 URL 이므로 본인의 URL 작성
            if(Hls.isSupported()) {
              var video = document.getElementById('video');
              var hls = new Hls();
              hls.loadSource(videoSrc); // 동영상경로
              hls.attachMedia(video);
              hls.on(Hls.Events.MANIFEST_PARSED,function() {
                  video.play();
              });
            }else if (video.canPlayType('application/vnd.apple.mpegurl')) {
              video.src = videoSrc; // 동영상경로
              video.addEventListener('play',function() {
                video.play();
              });
            }

            $('button[name=btn_play]').text("재생")
            $('button[name=btn_play]').addClass("btn-outline-success");
            $('button[name=btn_play]').removeClass("btn-outline-danger");
            btnObj.text("정지");
            btnObj.addClass("btn-outline-danger");
            btnObj.removeClass("btn-outline-success");
  
          }else{
            $.notify('<strong>실패</strong>', {type: 'danger'});
          }
        }
      });
    }else{
      fnPlayStop();
    }
    
  
  });

}

function albumModalView(id){
  
  var albumId = id;
  
  $.ajax({
    url: '/' + package_name + '/ajax/'+sub+'/albumInfo',
    type: "POST", 
    cache: false,
    data: {"albumId":albumId},
    dataType: "json",
    success: function (data) {
      if( data.ret == "success" ){
        
        $('#artistModal').modal('hide');
        
        $('.modalinnerbyAlbum').empty();
        $('.modalinnerbyAlbum').append( getAlbumModalHtml(data) );
        downloadEventAdd("album");
        $('#albumModal').modal();
        $('#albumModal').on('hide.bs.modal', function (e) {
          fnPlayStop();
        });
      }else{
        $.notify('<strong>조회 실패</strong>', {type: 'danger'});
      }
    }
  });
  
}
function getAlbumModalHtml(data){
  
  album = data.albumInfo.response.result.album;
  albumModalHtml = '';
  albumModalHtml += '<div class="modal fade" id="albumModal" tabindex="-1" role="dialog" aria-hidden="true">';
  albumModalHtml += '    <div class="modal-dialog modal-dialog-centered modal-lg" role="document">';
  albumModalHtml += '      <div class="modal-content">';
  albumModalHtml += '        <div class="modal-header">';
  albumModalHtml += '          <h5 class="modal-title" id="exampleModalLongTitle">'+album.albumTitle+'</h5>';
  albumModalHtml += '          <button type="button" class="close" data-dismiss="modal" aria-label="Close">';
  albumModalHtml += '            <span aria-hidden="true">&times;</span>';
  albumModalHtml += '          </button>';
  albumModalHtml += '        </div>';
  albumModalHtml += '        <div class="modal-body">';
  albumModalHtml += '          <div class="row pb-2"">';
  albumModalHtml += '            <div class="col-md-2">';
  albumModalHtml += '              <img src="'+album.imageUrl+'" class="rounded float-left w-100" alt="...">';
  albumModalHtml += '            </div>';
  albumModalHtml += '            <div class="col-md-8 ">';
  albumModalHtml += '              <div class="row">';

  if( album.artists.artist[0] == undefined ){
    artistName = album.artists.artist.artistName;
    artistId = album.artists.artist.artistId;
    albumModalHtml += '                <a href="#" alt = "'+artistId+'" class="alert-link text-dark artistView"><p class="text-left">'+artistName+'</p></a>';
  }else{
    for( var j in album.artists.artist){
      if( j > 0 ){
        albumModalHtml += ", ";
      }
      artistName = album.artists.artist[j].artistName;
      artistId = album.artists.artist[j].artistId;
      albumModalHtml += '                <a href="#" alt = "'+artistId+'" class="alert-link text-dark artistView"><p class="text-left">'+artistName+'</p></a>';
    }
  }
  
  albumModalHtml += '              </div>';
  albumModalHtml += '              <div class="row">';
  albumModalHtml += '                <p class="text-left">'+album.releaseDate+' '+album.albumGenres+'</p>';
  albumModalHtml += '              </div>';
  albumModalHtml += '            </div>';
  albumModalHtml += '          </div>';
  albumModalHtml += '          <hr style="width: 100%; margin:0px; background-color:#808080;" class="mb-2">';
  albumModalHtml += '          <div style="height: 300px; overflow-x: hidden;">';
  for( i = 0 ; i < data.albumTracks.response.result.trackTotalCount ; i++ ){
    track = data.albumTracks.response.result.tracks.track[i];
    if( track == undefined ){
      track = data.albumTracks.response.result.tracks.track;
    }
    albumModalHtml += '          <div class="row">';
    albumModalHtml += '            <div class="col-md-1 text-center">';
    albumModalHtml += '              '+track.trackNumber;;
    albumModalHtml += '            </div>';
    albumModalHtml += '            <div class="col-md-4">';
    albumModalHtml += '              '+track.trackTitle;
    albumModalHtml += '            </div>';
    albumModalHtml += '            <div class="col-md-4">';
    
    if( track.artists.artist[0] == undefined ){
      artistName = track.artists.artist.artistName;
      artistId = track.artists.artist.artistId;
      albumModalHtml += '                <a href="#" alt = "'+artistId+'" class="alert-link text-dark artistView">'+artistName+'</a>';
    }else{
      for( var j in track.artists.artist){
        if( j > 0 ){
          albumModalHtml += ", ";
        }
        artistName = track.artists.artist[j].artistName;
        artistId = track.artists.artist[j].artistId;
        albumModalHtml += '                <a href="#" alt = "'+artistId+'" class="alert-link text-dark artistView">'+artistName+'</a>';
      }
    }
    albumModalHtml += '            </div>';
    albumModalHtml += '            <div class="col-md-3 text-right pl-auto">';
    albumModalHtml += '              <div class="btn-group btn-group-sm flex-wrap mr-2" role="group">';
    albumModalHtml += '                <button id="btn_download" name="btn_download" class="btn btn-sm btn-outline-success" data-trackid="'+track.trackId+'">다운로드</button>';
    albumModalHtml += '                <button id="btn_play" name="btn_play" class="btn btn-sm btn-outline-success" data-trackid="'+track.trackId+'">재생</button>';
    albumModalHtml += '              </div>';
    albumModalHtml += '            </div>';
    albumModalHtml += '          </div>';
    albumModalHtml += '          <hr style="width: 100%; margin:0px;" class="my-2 .bg-secondary">';


  }
  albumModalHtml += '        </div>';
  albumModalHtml += '        </div>';
  albumModalHtml += '        <div class="modal-footer ">';
  albumModalHtml += '          <button id="btn_download_all" name="btn_download_all" class="btn btn-sm btn-outline-success" data-albumid="'+album.albumId+'">전체 다운로드</button>';
  albumModalHtml += '        </div>';
  albumModalHtml += '      </div>';
  albumModalHtml += '    </div>';
  albumModalHtml += '  </div>';

  return albumModalHtml;
}

function artistModalView(id){
  
  var artistId = id;
  
  $.ajax({
    url: '/' + package_name + '/ajax/'+sub+'/artistInfo',
    type: "POST", 
    cache: false,
    data: {"artistId":artistId},
    dataType: "json",
    success: function (data) {
      if( data.ret == "success" ){

        $('#albumModal').modal('hide');

        $('.modalinnerbyArtist').empty();
        $('.modalinnerbyArtist').append( getArtistModalHtml(data) );
        downloadEventAdd("artist");
        $('#artistModal').modal();
        $('#artistModal').on('hide.bs.modal', function (e) {
          fnPlayStop();
        });
      }else{
        $.notify('<strong>조회 실패</strong>', {type: 'danger'});
      }
    }
  });
  
}
function getArtistModalHtml(data){
  
  artist = data.artistInfo.response.result.artist;
  artistModalHtml = '';
  artistModalHtml += '<div class="modal fade" id="artistModal" tabindex="-1" role="dialog" aria-hidden="true">';
  artistModalHtml += '    <div class="modal-dialog modal-dialog-centered modal-lg" role="document" style="max-width: 1000px;">';
  artistModalHtml += '      <div class="modal-content">';
  artistModalHtml += '        <div class="modal-header">';
  artistModalHtml += '          <h5 class="modal-title" id="exampleModalLongTitle"></h5>';
  artistModalHtml += '          <button type="button" class="close" data-dismiss="modal" aria-label="Close">';
  artistModalHtml += '            <span aria-hidden="true">&times;</span>';
  artistModalHtml += '          </button>';
  artistModalHtml += '        </div>';
  artistModalHtml += '        <div class="modal-body">';
  artistModalHtml += '          <div class="row pb-2">';
  artistModalHtml += '            <div class="col-md-3">';
  artistModalHtml += '              <img src="'+artist.imageUrl+'" class="rounded float-left w-100" alt="..." onerror="artistImageErr(this);">';
  artistModalHtml += '            </div>';
  artistModalHtml += '            <div class="col-md-7 ">';
  artistModalHtml += '              <div class="row">';
  artistModalHtml += '                <p class="text-left"><h5>'+artist.artistName+'</h5></p>';
  artistModalHtml += '              </div>';
  artistModalHtml += '              <div class="row">';
  artistModalHtml += '                <p class="text-left">'+artist.genreNames+'</p>';
  artistModalHtml += '              </div>';
  artistModalHtml += '            </div>';
  artistModalHtml += '          </div>';
  artistModalHtml += '          <hr style="width: 100%; margin:0px; background-color:#808080;" class="mb-2">';
  artistModalHtml += '          <div style="height: 300px; overflow-x: hidden;">';
  
  
  
  if( data.artistTrack.response.result.trackTotalCount > 0 ){
    viewSize = $('#artistModal .modal-body > div:last .row').length;
    
    cnt = 0;
    if( data.artistTrack.response.result.tracks == null){
      cnt = 0;
    }else if( data.artistTrack.response.result.tracks.track[0] != undefined ){
      cnt = Object.keys(data.artistTrack.response.result.tracks.track).length;
    }else{
      cnt = 1;
    }
    for( i = 0 ; i < cnt ; i++ ){
      
    // for( i = 0 ; i < data.artistTrack.response.result.trackTotalCount ; i++ ){
      
      track = data.artistTrack.response.result.tracks.track[i];
      if( track == undefined ){
        track = data.artistTrack.response.result.tracks.track;
      }
      artistModalHtml += '          <div class="row">';
      artistModalHtml += '            <div class="col-md-3">';
      artistModalHtml += '              '+track.trackTitle;
      artistModalHtml += '            </div>';
      artistModalHtml += '            <div class="col-md-3">';
      
      if( track.artists != undefined ){
        if( track.artists.artist[0] == undefined ){
          artistName = track.artists.artist.artistName;
          artistId = track.artists.artist.artistId;
          artistModalHtml += '                <a href="#" alt = "'+artistId+'" class="alert-link text-dark artistView">'+artistName+'</a>';
        }else{
          for( var j in track.artists.artist){
            if( j > 0 ){
              artistModalHtml += ", ";
            }
            artistName = track.artists.artist[j].artistName;
            artistId = track.artists.artist[j].artistId;
            artistModalHtml += '                <a href="#" alt = "'+artistId+'" class="alert-link text-dark artistView">'+artistName+'</a>';
          }
        }
      }
      console.log("2");
      albumTitle = '';
      albumId = '';
      
      if( track.album != undefined ){
        albumId = track.album.albumId;
        albumTitle = track.album.albumTitle;
      }else if( track.albumId != undefined ){
        albumId = track.albumId;
        albumTitle = track.albumTitle;
      }
      console.log("3");
      artistModalHtml += '            </div>';
      artistModalHtml += '            <div class="col-md-4">';
      artistModalHtml += '              <a href="#" alt = "'+albumId+'" class="alert-link text-dark albumView">'+ albumTitle + '</a>';
      artistModalHtml += '            </div>';
      artistModalHtml += '            <div class="col-md-2 text-right pl-auto">';
      artistModalHtml += '              <div class="btn-group btn-group-sm flex-wrap mr-2" role="group">';
      artistModalHtml += '                <button id="btn_download" name="btn_download" class="btn btn-sm btn-outline-success" data-trackid="'+track.trackId+'">다운로드</button>';
      artistModalHtml += '                <button id="btn_play" name="btn_play" class="btn btn-sm btn-outline-success" data-trackid="'+track.trackId+'">재생</button>';
      artistModalHtml += '              </div>';
      artistModalHtml += '            </div>';
      artistModalHtml += '          </div>';
      artistModalHtml += '          <hr style="width: 100%; margin:0px;" class="my-2 .bg-secondary">';

      viewSize++;
    }
    // debugger
    // if( data.artistTrack.response.result.trackTotalCount > viewSize){
    //   artistModalHtml += '<div class="row">';
    //   artistModalHtml += '  <div class="container pt-4">';
    //   artistModalHtml += '   <div class="row justify-content-md-center">';
    //   artistModalHtml += '     <div class="col-md-auto">';
    //   artistModalHtml += '       <div class="btn-group btn-group-lg flex-wrap mr-2" role="group">';
    //   artistModalHtml += '        <button id="btn_add_view_track" name="btn_add_view_track" class="btn btn-lg btn-outline-primary" data-row="'+viewSize+'">더보기</button>';
    //   artistModalHtml += '       </div>';
    //   artistModalHtml += '     </div>';
    //   artistModalHtml += '   </div>';
    //   artistModalHtml += '  </div>';
    //   artistModalHtml += '</div>';
    // }
  }
  
  artistModalHtml += '            </div>';
  artistModalHtml += '        </div>';
  artistModalHtml += '        <div class="modal-footer ">';
  artistModalHtml += '          <button id="btn_download_all" name="btn_download_all" class="btn btn-sm btn-outline-success" data-artistid="'+artist.artistId+'">전체 다운로드</button>';
  artistModalHtml += '        </div>';
  artistModalHtml += '      </div>';
  artistModalHtml += '    </div>';
  artistModalHtml += '  </div>';

  return artistModalHtml;
}
function artistImageErr(obj){
  obj.src ="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS2I0cfUaQK7bSG8L8q4cImt2i0qhd6XwNdeg&usqp=CAU";
}
function fnPlayStop(){
  $('button[name=btn_play]').text("재생")
  $('button[name=btn_play]').addClass("btn-outline-success");
  $('button[name=btn_play]').removeClass("btn-outline-danger");
  document.getElementById('video').pause();
}