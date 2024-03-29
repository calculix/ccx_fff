!
!     CalculiX - A 3-dimensional finite element program
!              Copyright (C) 1998 Guido Dhondt
!
!     This program is free software; you can redistribute it and/or
!     modify it under the terms of the GNU General Public License as
!     published by the Free Software Foundation(version 2);
!
!
!     This program is distributed in the hope that it will be useful,
!     but WITHOUT ANY WARRANTY; without even the implied warranty of
!     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
!     GNU General Public License for more details.
!
!     You should have received a copy of the GNU General Public License
!     along with this program; if not, write to the Free Software
!     Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
!
      subroutine generatetet_refine(kontet,ifatet,ifreetet,bc,ifac,&
        itetfa,ifreefa,planfa,ipofa,nodes,cotet,cg)
      !
      implicit none
      !
      integer nodes(4),nodef(3),kontet(4,*),ifatet(4,*),ifac(4,*),&
        itetfa(2,*),ipofa(*),ifreetet,ifreefa,ig(3,4),index,i,n,kflag,&
        node,ielement
      !
      real*8 bc(4,*),planfa(4,*),cotet(3,*),cg(3,*),&
        p1x,p1y,p1z,p2x,p2y,p2z,p3x,p3y,p3z,p4x,p4y,p4z,a11,&
        a12,a13,a21,a22,a23,a31,a32,a33,d1,d2,d3,det,x,y,z,r,dd
      !
      data ig /2,3,4,3,4,1,4,1,2,1,2,3/
      !
      !     updating the node per element relationship
      !
      ielement=ifreetet
      ifreetet=kontet(4,ielement)
      if(ifreetet.eq.0) then
         write(*,*) '*ERROR in generatetet_refine increase the dimension'              '*ERROR in generatetet_refine increase the dimension'
         write(*,*) '       of kontet'
         call exit(201)
      endif
      !
      do i=1,4
         kontet(i,ielement)=nodes(i)
      enddo
      !
      !     creating faces
      !
      do i=1,4
         nodef(1)=nodes(ig(1,i))
         nodef(2)=nodes(ig(2,i))
         nodef(3)=nodes(ig(3,i))
         !
         n=3
         kflag=1
         call insertsorti(nodef,n)
         !
         !        check whether face already exists
         !
         node=nodef(1)
         index=ipofa(node)
         !
         do
            if(index.eq.0) exit
            if((ifac(2,index).eq.nodef(2)).and.&
               (ifac(3,index).eq.nodef(3))) exit
            index=ifac(4,index)
         enddo
         !
         if(index.eq.0) then
            index=ifreefa
            ifreefa=ifac(4,ifreefa)
            if(ifreefa.eq.0) then
               write(*,*) '*ERROR in generatetet_refine increase the dimension'                 '*ERROR in generatetet_refine increase the dimension'
               write(*,*) '       of ifac'
               call exit(201)
            endif
            ifac(1,index)=nodef(1)
            ifac(2,index)=nodef(2)
            ifac(3,index)=nodef(3)
            itetfa(1,index)=ielement
            ifac(4,index)=ipofa(node)
            ipofa(node)=index
            !
            call planeeq(cotet,nodef,planfa(1,index))
         !
         else
            if(itetfa(1,index).eq.0) then
               itetfa(1,index)=ielement
            else
               itetfa(2,index)=ielement
            endif
         endif
         !
         !        the face number in ifatet is negative, if the equation
         !        of the face plane is such, that its value in the
         !        remaining node of the tetrahedron is negative
         !
         dd=planfa(1,index)*cotet(1,nodes(i))+&
            planfa(2,index)*cotet(2,nodes(i))+&
            planfa(3,index)*cotet(3,nodes(i))+&
            planfa(4,index)
         if(dd.ge.0.d0) then
            ifatet(i,ielement)=index
         else
            ifatet(i,ielement)=-index
         endif
      enddo
      !
      !     finding the center and radius of the circumscribed sphere
      !
      p1x=cotet(1,nodes(1))
      p1y=cotet(2,nodes(1))
      p1z=cotet(3,nodes(1))
      !
      p2x=cotet(1,nodes(2))
      p2y=cotet(2,nodes(2))
      p2z=cotet(3,nodes(2))
      !
      p3x=cotet(1,nodes(3))
      p3y=cotet(2,nodes(3))
      p3z=cotet(3,nodes(3))
      !
      p4x=cotet(1,nodes(4))
      p4y=cotet(2,nodes(4))
      p4z=cotet(3,nodes(4))
      !
      a11=p1x-p2x
      a12=p1y-p2y
      a13=p1z-p2z
      d1=((p1x+p2x)*a11+(p1y+p2y)*a12+(p1z+p2z)*a13)/2.d0
      !
      a21=p1x-p3x
      a22=p1y-p3y
      a23=p1z-p3z
      d2=((p1x+p3x)*a21+(p1y+p3y)*a22+(p1z+p3z)*a23)/2.d0
      !
      a31=p1x-p4x
      a32=p1y-p4y
      a33=p1z-p4z
      d3=((p1x+p4x)*a31+(p1y+p4y)*a32+(p1z+p4z)*a33)/2.d0
      !
      det=a11*(a22*a33-a32*a23)-a12*(a21*a33-a31*a23)+&
           a13*(a21*a32-a31*a22)
      x=(d1*(a22*a33-a23*a32)-d2*(a12*a33-a32*a13)+&
           d3*(a12*a23-a22*a13))/det
      y=(-d1*(a21*a33-a31*a23)+d2*(a11*a33-a31*a13)-&
           d3*(a11*a23-a21*a13))/det
      z=(d1*(a21*a32-a31*a22)-d2*(a11*a32-a31*a12)+&
             d3*(a11*a22-a21*a12))/det
      !
      r=dsqrt((x-p1x)**2+(y-p1y)**2+(z-p1z)**2)
      !
      bc(1,ielement)=x
      bc(2,ielement)=y
      bc(3,ielement)=z
      bc(4,ielement)=r
      !
      !     determining the center of gravity of the element
      !
      cg(1,ielement)=(p1x+p2x+p3x+p4x)/4.d0
      cg(2,ielement)=(p1y+p2y+p3y+p4y)/4.d0
      cg(3,ielement)=(p1z+p2z+p3z+p4z)/4.d0
      !
      return
      end
