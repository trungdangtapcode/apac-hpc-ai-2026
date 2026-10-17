class Slide:
    def __init__(self,title,source='',notes='',cover=False,dark=False):
        self.s=prs.slides.add_slide(prs.slide_layouts[6]);self.n=len(prs.slides)
        self.title=title;self.source=source;self.lines=[];self.notes=notes;self.bg=INK if dark else PAPER
        self.s.background.fill.solid();self.s.background.fill.fore_color.rgb=rgb(self.bg)
        pdf.setFillColor(HexColor(self.bg));pdf.rect(0,0,W*72,H*72,fill=1,stroke=0)
        background=BACKGROUNDS[self.n-1]
        self.image(EXTERNAL/background['file'],0,0,W,H,crop=True,focus=background['focus'])
        if dark:self.gradient_rect(0,0,W,H,INK,'#355D68',.92,.84)
        else:self.gradient_rect(0,0,W,H,PAPER,'#F3F7F7',.91,.82)
        if not cover:
            self.gradient_rect(0,0,W,.84,INK,'#375C6A')
            self.text(title,.66,.21,12,.46,26,WHITE)
        # Quiet footer; progress bar is the Metropolis visual signature.
        # Submission provenance is metadata, not audience-facing slide text.
        self.text('TripleU  /  APAC HPC-AI 2026',.66,7.10,8,.20,9,GRAY if not dark else '#B5C1C3')
        self.text(f'{self.n:02d}',12.18,7.06,.5,.28,11,GRAY if not dark else '#B5C1C3')
        self.rect(0,7.465,W,.035,PALE if not dark else '#3F5459')
        self.rect(0,7.465,W*self.n/32,.035,ORANGE)
    def rect(self,x,y,w,h,fill,stroke=None,width=1):
        shape=self.s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
        if fill:shape.fill.solid();shape.fill.fore_color.rgb=rgb(fill)
        else:shape.fill.background()
        if stroke:shape.line.color.rgb=rgb(stroke);shape.line.width=Pt(width)
        else:shape.line.fill.background()
        if fill:pdf.setFillColor(HexColor(fill))
        if stroke:pdf.setStrokeColor(HexColor(stroke));pdf.setLineWidth(width)
        pdf.rect(x*72,(H-y-h)*72,w*72,h*72,fill=int(bool(fill)),stroke=int(bool(stroke)))
        return shape
    def gradient_rect(self,x,y,w,h,start,end,start_alpha=1,end_alpha=1):
        shape=self.s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
        shape.line.fill.background();shape.fill.gradient();shape.fill.gradient_angle=0
        for stop,color,alpha in zip(shape.fill.gradient_stops,(start,end),(start_alpha,end_alpha)):
            stop.color.rgb=rgb(color)
            clr=stop._gs.find('{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr')
            opacity=OxmlElement('a:alpha');opacity.set('val',str(round(alpha*100000)));clr.append(opacity)
        pdf.saveState()
        if start_alpha==end_alpha==1:
            clip=pdf.beginPath();clip.rect(x*72,(H-y-h)*72,w*72,h*72);pdf.clipPath(clip,stroke=0)
            pdf.linearGradient(x*72,(H-y)*72,(x+w)*72,(H-y)*72,[HexColor(start),HexColor(end)])
        else:
            # Render one continuous alpha overlay for the PDF. Adjacent
            # translucent vector strips can show antialiasing seams.
            # The PPTX uses the editable native gradient above, and original
            # photographs are never raster-edited or flattened into the tint.
            a=np.array([int(start[i:i+2],16) for i in (1,3,5)])/255
            b=np.array([int(end[i:i+2],16) for i in (1,3,5)])/255
            samples=np.linspace(0,1,2048)
            colors=(a[None,:]*(1-samples[:,None])+b[None,:]*samples[:,None])*255
            alpha=(start_alpha*(1-samples)+end_alpha*samples)*255
            row=np.column_stack((colors,alpha)).round().astype(np.uint8)
            overlay=Image.fromarray(np.broadcast_to(row[None,:,:],(2,2048,4)).copy())
            pdf.drawImage(ImageReader(overlay),x*72,(H-y-h)*72,w*72,h*72,mask='auto')
        pdf.restoreState()
        return shape
    def line(self,x1,y1,x2,y2,color=INK,width=1.2):
        shape=self.s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x1),Inches(y1),Inches(x2),Inches(y2))
        shape.line.color.rgb=rgb(color);shape.line.width=Pt(width)
        pdf.setStrokeColor(HexColor(color));pdf.setLineWidth(width);pdf.line(x1*72,(H-y1)*72,x2*72,(H-y2)*72)
    def arrow(self,x1,y1,x2,y2,color=INK,width=1.7):
        self.line(x1,y1,x2-.10,y2,color,width)
        triangle=self.s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE,Inches(x2-.14),Inches(y2-.075),Inches(.15),Inches(.15))
        triangle.rotation=90;triangle.fill.solid();triangle.fill.fore_color.rgb=rgb(color);triangle.line.fill.background()
        path=pdf.beginPath();path.moveTo(x2*72,(H-y2)*72);path.lineTo((x2-.13)*72,(H-y2+.07)*72);path.lineTo((x2-.13)*72,(H-y2-.07)*72);path.close()
        pdf.setFillColor(HexColor(color));pdf.drawPath(path,fill=1,stroke=0)
    def text(self,text,x,y,w,h,size=20,color=INK,bold=False,mono=False):
        fam=MONO if mono else BOLD if bold else FONT
        lines=[]
        for paragraph in str(text).split('\n'):
            if not paragraph:lines.append('');continue
            current=''
            for word in paragraph.split():
                candidate=(current+' '+word).strip()
                if pdfmetrics.stringWidth(candidate,fam,size)>w*72 and current:lines.append(current);current=word
                else:current=candidate
            lines.append(current)
        leading=size*1.18
        if leading*len(lines)>h*72+.5:raise ValueError(f'Slide {self.n} text overflow: {text!r} ({leading*len(lines):.1f}>{h*72:.1f})')
        for line in lines:
            if pdfmetrics.stringWidth(line,fam,size)>w*72+.5:raise ValueError(f'Slide {self.n} unbreakable word overflow: {line}')
        box=self.s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=box.text_frame
        tf.clear();tf.word_wrap=False;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
        for i,line in enumerate(lines):
            p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line
            p.font.name='Courier New' if mono else 'Arial';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=rgb(color)
            p.space_before=p.space_after=Pt(0);p.line_spacing=Pt(leading)
            pdf.setFont(fam,size);pdf.setFillColor(HexColor(color));pdf.drawString(x*72,(H-y)*72-size*.94-i*leading,line)
        self.lines.append(str(text));bounds.append({'slide':self.n,'x':x,'y':y,'w':w,'h':h,'text':str(text)})
        return box
    def image(self,path,x,y,w,h,crop=False,focus=.5):
        iw,ih=Image.open(path).size
        if not crop:
            scale=min(w/iw,h/ih);pw,ph=iw*scale,ih*scale;px=x+(w-pw)/2;py=y+(h-ph)/2
            self.s.shapes.add_picture(str(path),Inches(px),Inches(py),Inches(pw),Inches(ph))
            pdf.drawImage(str(path),px*72,(H-py-ph)*72,pw*72,ph*72,mask='auto')
        else:
            fraction=min(1,(w/h)/(iw/ih));vfrac=min(1,(iw/ih)/(w/h))
            left=max(0,min(1-fraction,focus-fraction/2));right=1-left-fraction;top=(1-vfrac)/2
            picture=self.s.shapes.add_picture(str(path),Inches(x),Inches(y),Inches(w),Inches(h));picture.crop_left=left;picture.crop_right=right
            picture.crop_top=picture.crop_bottom=top
            pdf.saveState();clip=pdf.beginPath();clip.rect(x*72,(H-y-h)*72,w*72,h*72);pdf.clipPath(clip,stroke=0)
            fullw=w/fraction;fullh=h/vfrac
            pdf.drawImage(str(path),(x-left*fullw)*72,(H-y-h-top*fullh)*72,fullw*72,fullh*72);pdf.restoreState()
    def icon(self,name,x,y,size=.45):self.image(EXTERNAL/(name+'.png'),x,y,size,size)
    def chips(self,x,y,count,size=.37,color=ORANGE,gap=.12):
        for i in range(count):
            self.rect(x+i*(size+gap),y,size,size,None,color,1.5)
            self.rect(x+i*(size+gap)+.11,y+.11,size-.22,size-.22,color)
    def end(self):
        self.s.notes_slide.notes_text_frame.text=self.notes
        outline.append({'number':self.n,'title':self.title,'text':self.lines,'speaker_notes_en':self.notes})
        pdf.showPage()

