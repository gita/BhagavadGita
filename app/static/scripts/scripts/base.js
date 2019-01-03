<script type="text/javascript" src="https://platform-api.sharethis.com/js/sharethis.js#property=5a8d87d4d57467001383cda2&product=inline-share-buttons" defer></script>

        <script>
          function setCookie(name,value,days) {
              var expires = "";
              if (days) {
                  var date = new Date();
                  date.setTime(date.getTime() + (days*24*60*60*1000));
                  expires = "; expires=" + date.toUTCString();
              }
              document.cookie = name + "=" + (value || "")  + expires + "; path=/";
          }

          function getCookie(name) {
              var nameEQ = name + "=";
              var ca = document.cookie.split(';');
              for(var i=0;i < ca.length;i++) {
                  var c = ca[i];
                  while (c.charAt(0)==' ') c = c.substring(1,c.length);
                  if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
              }
              return null;
          }
          function eraseCookie(name) {
              document.cookie = name+'=; Max-Age=-99999999;';
          }

          if ({{current_user.is_authenticated|tojson}} === false) {
            if (document.cookie.indexOf("visits=") >= 0) {
              var visits = JSON.parse(getCookie('visits'));
              if (visits%10 === 0) {$(goloka).modal()}
              setCookie('visits',visits+1,30);
            } else {
              setCookie('visits',1,30);
            }
          }

          if (document.cookie.indexOf("settings=") >= 0) {
            var settings = JSON.parse(getCookie('settings'));
            if (settings['theme']) {
              if (settings['theme'] == "Dark") {
                $('body').append(`<style id="dark">body{color:#fff;background-color:#121212}.amber.darken-2,.card,.card-body,.modal-content{background-color:#232323!important}.card .card-text{color:#BDBDBD}hr{border-top:1px solid #616161}.sidenav{background-color:#1C1C1C}.sidenav li>a{color:#fff}#mobile-demo>li>a.active,.sidenav .collapsible-header:hover,.sidenav li>a:hover{background-color:#474747}.dropdown-menu{background-color:#1C1C1C}.navbar .dropdown-menu a{color:#fff!important}.navbar .dropdown-menu a:hover{background-color:#474747;color:#fff!important}.select2-container--default .select2-selection--single{background-color:#474747}#email,#first_name,#last_name,#password,#password2,.close,.close:hover,.modal-content,.pagination a,.select2-container--default .select2-selection--single .select2-selection__rendered{color:#fff}.modal-footer{border-top:none!important}</style>`)
              }
            }
          }

          $(document).ready(function() {
            $('.sidenav').sidenav();
            $('.collapsible').collapsible();
            $('.dropdown-trigger').dropdown();

            var ua = navigator.userAgent.toLowerCase();
            var isAndroid = ua.indexOf("bhagavadgita") > -1;
            if (isAndroid) {
              $('#gita').append(`<div class="dropdown-divider"></div>`)
              $('#gita').append(`<a class="dropdown-item waves-effect waves-light" data-toggle="modal" data-target="#vishnu" id="sharevishnu">Share</a>`)
              $('#gita').append(`<a class="dropdown-item waves-effect waves-light" href="https://bhagavadgita.io/about/" target="_blank">About Bhagavad Gita</a>`)
              // $('#gita').append(`<a class="dropdown-item waves-effect waves-light" data-toggle="modal" data-target="#shiva">About</a>`)
              $('#bhagavadgitafooter').remove();
            }


            if (['/account/register', '/account/login', '/account/reset-password', '/account/manage/info', '/account/manage/change-email', '/account/manage/change-password', '/account/manage/apps', '/account/manage/apps/new', '/reading-plans/', '/favourite-shlokas/', '/progress/', '/badges/', '/account/unconfirmed'].indexOf(window.location.pathname) >= 0) {
              $('#bhagavadgitafooter').remove()
            }

            $(window).scroll(function() {
              if ($(this).scrollTop() > 200) {
                $('.go-top').fadeIn(200);
              } else {
                $('.go-top').fadeOut(200);
              }
            });
            $('.go-top').click(function(event) {
              event.preventDefault();

              $('html, body').animate({scrollTop: 0}, 300);
            })
          });

          const badge_list = {{badge_list|safe}}
          if (badge_list != []) {
            for (const s of badge_list) {
              var vrindavan = '#vrindavan' + s['badge_id']
              $(vrindavan).modal()
            }
          }

          $('#whatsappbtn, #facebookbtn, #twitterbtn').click(function() { share() })

          function share() {
            axios.get("/share")
            .then(function (response) {
                $('body').append(`<div class="modal fade" id="vrindavan` + response.data[0].badge_id + `" tabindex="-1" role="dialog" aria-hidden="true"> <div class="modal-dialog modal-dialog-centered" role="document"> <div class="modal-content"> <div class="modal-header text-center" style="border-bottom: none"> <h5 class="modal-title w-100" id="vrindavanTitle">{{_('Achievement Unlocked')}}</h5> <button type="button" class="close" data-dismiss="modal" aria-label="Close"> <span aria-hidden="true">&times;</span> </button> </div><div class="modal-body"> <div align="center"> <img src="` + response.data[0].badge_image + `" alt="Complete" height="100" width="100"> <h5>` + response.data[0].badge_name + `</h5> <br><p>` + response.data[0].badge_description + `</p><p> <b>Jai Shri Krishna!</b> </p></div></div></div></div></div>`)
                const badge_list = response.data
                if (badge_list != []) {
                  for (const s of badge_list) {
                    var vrindavan = '#vrindavan' + response.data[0].badge_id
                    $(vrindavan).modal()
                  }
                }
            })
          }
        </script>