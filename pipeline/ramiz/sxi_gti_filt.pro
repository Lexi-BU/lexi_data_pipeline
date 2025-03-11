PRO sxi_gti_filt,gti_file,time_stmp,frac

;auth: kdkvp
;date: 17/02/24
;purp: determines fraction of each time step that is included in the GTI
;mods:
;TBDS:
;inpt: 
;      gti_file  : name of input GTI file
;      time_stmp : list beginning times of intervals (also end time of last)
;otpt:
;      frac      : fraction of each interval that is good

; time_stmp: the time at the beginning of each time interval (s)

; read the GTI file
  gti=mrdfits(gti_file,'GTI')
  n_gti=n_elements(gti)

  n_time=n_elements(time_stmp)
  frac=fltarr(n_time)
  g_indx=0 ; first GTI index
  t_indx=0 ; first time index

  f_time=time_stmp(t_indx)
  while(f_time LT gti(n_gti-1).stop AND t_indx LT n_time-1 $
    AND g_indx LT n_gti)do begin
    case(1)of
    (f_time LT gti(g_indx).start):begin
      case(1)of
        (time_stmp(t_indx+1) LT gti(g_indx).start): begin
          ;frac(t_indx)=frac(t_indx)+0.0
          ;print,'a',t_indx,frac(t_indx)
          t_indx=t_indx+1
          f_time=time_stmp(t_indx)
          end
        (time_stmp(t_indx+1) GT gti(g_indx).stop): begin
          frac(t_indx)=frac(t_indx)+gti(g_indx).stop-gti(g_indx).start
          print,'b',t_indx,frac(t_indx)
          g_indx=g_indx+1
          end
        else: begin
          frac(t_indx)=frac(t_indx)+time_stmp(t_indx+1)-gti(g_indx).start
          print,'c',t_indx,frac(t_indx)
          t_indx=t_indx+1
          f_time=time_stmp(t_indx)
          end
      endcase
      end
    (f_time GE gti(g_indx).start AND f_time LT gti(g_indx).stop):begin
      case(1)of
        (time_stmp(t_indx+1) LT gti(g_indx).stop):begin
          test=frac(t_indx)
          frac(t_indx)=frac(t_indx)+float(time_stmp(t_indx+1)-time_stmp(t_indx))
          print,'d',t_indx,test,frac(t_indx),float(time_stmp(t_indx+1)-time_stmp(t_indx))
          t_indx=t_indx+1
          f_time=time_stmp(t_indx)
          end
        else: begin
          frac(t_indx)=frac(t_indx)+gti(g_indx).stop-f_time
          print,'e',t_indx,frac(t_indx)
          g_indx=g_indx+1
          end
      endcase
      end
    (f_time GE gti(g_indx).stop):begin
      g_indx=g_indx+1
      end
    endcase
  endwhile

  !x.range=[min([time_stmp(0),gti(0).start]),$
     max([time_stmp(n_time-1),gti(n_gti-1).stop])]
  off=!x.range(0)
  !x.range=!x.range-off
  !y.range=[0,1]
  plot,[0,0],[0,0]
  for i=0,n_time-1 do oplot,time_stmp(i)-off*[1,1],[0.4,0.6]
  for i=0,n_gti-1 do oplot,gti(i).start-off*[1,1],[0.2,0.4],color=220
  for i=0,n_gti-1 do oplot,gti(i).stop-off*[1,1],[0.2,0.4],color=60
  oplot,time_stmp-off,frac/600.,psym=6,color=120

  end

