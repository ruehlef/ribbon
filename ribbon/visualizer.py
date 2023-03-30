import snappy 
from spherogram.links.orthogonal import *
from plink.editor import LinkDisplay
from plink.manager import LinkManager
from plink.viewer import LinkViewer
from plink.editor import PLinkBase
import numpy as np
from plink.gui import *
import tkinter

def custom_shift(self, dx, dy):
    pass

def custom_update_info(self):
    #self.style_var.set("pl")
    self.hide_DT()
    self.hide_labels()
    self.clear_text()
    if not self._check_update():
        return
    if self.show_DT_var.get():
        dt = self.DT_code()
        if dt is not None:
            self.show_DT()
    if self.show_labels_var.get():
        self.show_labels()
    self.show_faces()
    ulx, uly, lrx, lry = self.canvas.bbox('transformable')
    self.labels.append(self.canvas.create_text(
                (10, 10),
                anchor=Tk_.W,
                text=self.band_string, width = lrx - ulx
                ))
    info_value = self.info_var.get()
    if info_value == 1:
        self.DT_normal()
    elif info_value == 2:
        self.DT_alpha()
    elif info_value == 3:
        self.Gauss_info()
    elif info_value == 4:
        self.PD_info()
    elif info_value == 5:
        self.BB_info()

def custom_zoom(self, xfactor, yfactor):
    try:
        ulx, uly, lrx, lry = self.canvas.bbox('transformable')
    except TypeError:
        return
    for vertex in self.Vertices:
        vertex.x = ulx + xfactor*(vertex.x - ulx)
        vertex.y = uly + yfactor*(vertex.y - uly)
    self.update_crosspoints()
    for arrow in self.Arrows:
        arrow.draw(self.Crossings, skip_frozen=False)
    for vertex in self.Vertices:
        vertex.draw(skip_frozen=False)
    self.update_smooth()
    for livearrow in (self.LiveArrow1, self.LiveArrow2):
        if livearrow:
            x0,y0,x1,y1 = self.canvas.coords(livearrow)
            x0 = ulx + xfactor*(x0 - ulx)
            y0 = uly + yfactor*(y0 - uly)
            self.canvas.coords(livearrow, x0, y0, x1, y1)

    self.face_labels = [(p[0],(xfactor*(p[1][0]-ulx)+ulx,yfactor*(p[1][1]-uly)+uly)) for p in self.face_labels]
    self.update_info()
    W, H = self.canvas.winfo_width(), self.canvas.winfo_height()
    if W < 10:
        W, H = self.canvas.winfo_reqwidth(), self.canvas.winfo_reqheight()
    try:
        x0, y0, x1, y1 = self.canvas.bbox('transformable')
        self._shift( (W - x1 + x0)/2 - x0, (H - y1 + y0)/2 - y0 )
    except TypeError:
        pass

def show_faces(self):
    """
    Display the assigned labels next to each crossing.
    """

    for face_label, pt in self.face_labels:
        x,y = pt
        self.labels.append(self.canvas.create_text(
                (x, y),
                anchor=Tk_.W,
                text=str(face_label)
                ))
    

PLinkBase.show_faces = show_faces
PLinkBase.update_info = custom_update_info
LinkViewer.update_info = custom_update_info
PLinkBase._zoom = custom_zoom
PLinkBase._shift = custom_shift

def make_edge_and_face_to_crossings(edges, vertices):
    ef2c = {}
    for e in range(len(edges)):
        ef2c[e] = {}

    for face in vertices:
        face_as_list = list(face)
        fn = len(face_as_list)
        for i in range(fn):
            j = (i - 1) % fn
            crossing = face_as_list[i][0]  # global crossing label
            index = face_as_list[i][1]  # local index label, 0 is incoming understrand, then counterclock to 3
            e = crossing.strand_labels[index]
            ef2c[e][face] = ((face_as_list[i][0], face_as_list[i][1]), (face_as_list[j][0], (face_as_list[j][1] + 1) % 4))

    return ef2c

def visualize(L, filename, band_string = "", k=20, bump=1):
    
    
    G = L.dual_graph()
    edges, vertices = sorted(list(G.edges), key=lambda x: x.label), sorted(list(G.vertices), key=lambda x: x.label)
    ef2c = make_edge_and_face_to_crossings(edges,vertices)

    vertices, arrows, crossings = OrthogonalLinkDiagram(L).plink_data()
    link_manager = LinkManager()
    LinkManager.unpickle(link_manager,vertices, arrows, crossings)
    
    this_crossing, prev_crossing, first_crossing = str(-1), str(-1), str(-1)
    face_labels, cdict = [], {(c.x,c.y): [] for c in link_manager.Crossings}
    for idx, arrow in enumerate(link_manager.Arrows+[link_manager.Arrows[0],link_manager.Arrows[1]]):
        v0, v1 = np.array([arrow.start.x,arrow.start.y]), np.array([arrow.end.x,arrow.end.y])
        dv = (v1-v0)/k
        dvp = np.array([dv[1],-dv[0]])
        for l in range(k):
            this_pt, next_pt = v0+l*dv, v0+(l+1)*dv
            #tp2, tpidx = 0.0, len(knot_points)-1 # handles if this pt is a crossing
            if l+1 <= k: # if we're not done, check whether a crossing is in between
                for c in link_manager.Crossings:
                    if arrow in (c.over, c.under):
                        cv = np.array([c.x,c.y])
                        dtc, dnc, dtn = np.dot(this_pt-cv,this_pt-cv), np.dot(next_pt-cv,next_pt-cv), np.dot(this_pt-next_pt,this_pt-next_pt)
                        if (dtc < dtn and dnc < dtn) or np.array_equal(this_pt,cv):
                            #print("crossing",cv)
                            prev_crossing = this_crossing
                            if str(prev_crossing) == str(-1):
                                first_crossing = str(c.label)
                            this_crossing = str(c.label)
                            if str(-1) not in (str(prev_crossing), str(this_crossing)):
                                for fs in ef2c.values():
                                    #print(fs)
                                    for f, cr in fs.items():
                                        c1, c2 = cr[0][0], cr[1][0]
                                        c1l, c2l = str(c1.label), str(c2.label)
                                        if (c1l, c2l) == (prev_crossing, this_crossing) and arrow == c.under and cr[1][1]%2 == 0:
                                            #print("cross under",cv,f.label, prev_crossing, this_crossing)
                                            if f.label not in cdict[(cv[0],cv[1])]:
                                                face_labels.append((f.label,(cv-bump*(dv-dvp)).tolist()))
                                                cdict[(cv[0],cv[1])].append(f.label)
                                        if (c1l,c2l) == (prev_crossing, this_crossing) and arrow == c.over  and cr[1][1]%2 == 1:
                                            #print("cross over",cv,f.label, prev_crossing, this_crossing)
                                            if f.label not in cdict[(cv[0],cv[1])]:
                                                face_labels.append((f.label,(cv-bump*(dv-dvp)).tolist()))
                                                cdict[(cv[0],cv[1])].append(f.label)
                                        if (c1l,c2l) == (this_crossing, prev_crossing) and arrow == c.under and cr[1][1]%2 == 1:
                                            #print("cross under",cv,f.label, prev_crossing, this_crossing)
                                            if f.label not in cdict[(cv[0],cv[1])]:
                                                face_labels.append((f.label,(cv-bump*(dv+dvp)).tolist()))
                                                cdict[(cv[0],cv[1])].append(f.label)
                                        if (c1l,c2l) == (this_crossing, prev_crossing) and arrow == c.over  and cr[1][1]%2 == 0:
                                            #print("cross over",cv,f.label, prev_crossing, this_crossing)
                                            if f.label not in cdict[(cv[0],cv[1])]:
                                                face_labels.append((f.label,(cv-bump*(dv+dvp)).tolist()))
                                                cdict[(cv[0],cv[1])].append(f.label)

    #print(cdict)
    viewer = plink.LinkDisplay(show_crossing_labels=True, root=None)
    viewer.band_string = band_string
    viewer.face_labels = face_labels
    viewer.unpickle(vertices, arrows, crossings)
    viewer.update_info()
    # viewer.canvas.pack()
    # viewer.canvas.update()

    viewer._zoom(5,5)
    
    
    #ulx, uly, lrx, lry = viewer.canvas.bbox("transformable")
    #viewer.canvas.postscript(file=filename, x=ulx, y=uly, width=lrx-ulx, height=lry-uly, pagewidth=500)
    viewer.save_as_eps(filename)
