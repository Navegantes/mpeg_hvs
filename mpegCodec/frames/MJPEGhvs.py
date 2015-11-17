# -*- coding: utf-8 -*-
"""
Created on Thu Apr 02 19:28:28 2015

@author: Navegantes
"""

import huffcoder as h
import numpy as np
import cv2

class Encoder:
	def __init__(self, frame, qually, hufftables, Ztab, hvsqm, mode='444'):
		'''
		'''
		
		#TRATA AS DIMENSOES DA IMAGEM
		(self.Madj, self.Nadj, self.Dadj), self.img = h.adjImg(np.float32(frame))         #		imOrig = frame  #cv2.imread(filepath,1)        #self.filepath = filepath
		self.mode = mode
		self.hufftables = hufftables
		self.CRate = 0; self.Redunc = 0                #Taxa de compressão e Redundancia
		self.avgBits = 0; self.NumBits = 0             #Media de bits e numero de bits
		self.qually = qually                           #Qualidade
		self.M, self.N, self.D = frame.shape           #imOrig.shape          #Dimensões da imagem original
		self.r, self.c = [8, 8]                        #DIMENSAO DOS BLOCOS
		self.mbr, self.mbc = [16, 16]
		
		#NUMERO DE BLOCOS NA VERTICAL E HORIZONTAL
		self.nBlkRows = int(np.floor(self.Madj/self.mbr))
		self.nBlkCols = int(np.floor(self.Nadj/self.mbc))
		
		#GERA TABELA DE QUANTIZAÇÃO
#		self.hvsqm = Ztab[0]
#		if self.hvsqm==True:
		self.Zhvs = Ztab[0]
		self.MV = Ztab[1]
		self.sspace = Ztab[2]
#		else:
#			self.Z = Ztab[1]
		
		#TRANSFORMA DE RGB PARA YCbCr
		self.Ymg = self.img #cv2.cvtColor(self.img, cv2.COLOR_BGR2YCR_CB)
		
		if self.D == 2:
			self.NCHNL = 1
		elif self.D == 3:
			self.NCHNL = 3
			
		self.seqhuff = self._run_()
								
	def _run_(self):
		'''
		'''
		
		hf = h.HuffCoDec(self.hufftables)        #flnm = self.filepath.split('/')[-1:][0].split('.')[0] + '.huff'        #fo = open(flnm,'w')        #fo.write(str(self.Mo) + ',' + str(self.No) + ',' + str(self.Do) + ',' +         #         str(self.qually) + ',' + self.mode + '\n')
		outseq = []
		
#		dYmg = self.Ymg - 128
		dYmg = self.Ymg - 128
		r, c, chnl = self.r, self.c, self.NCHNL
		coefs = np.zeros((r, c, chnl))
		seqhuff = ''        #nbits = self.NumBits
		if self.mode == '444':
			for ch in range(chnl):
				DCant = 0
				vec = 0
				for x in range(0, self.Madj, self.mbr):
					for y in range(0, self.Nadj, self.mbc):
						#SELEÇAO DE TABELA
#						print int(self.MV[vec][0]),'/',int(self.MV[vec][1])
#						print len(self.MV), vec, self.MV[vec][0], self.MV[vec][1]
						Z = self.Zhvs[ int(abs(self.MV[vec][0])) ][ int(abs(self.MV[vec][1])) ]
#						print Z,
						for i in range(x, x+self.mbr, self.r):
							for j in range(y, y+self.mbc, self.c):
								sbimg = dYmg[i:i+self.r, j:j+self.c, ch]     #Subimagens nxn
								#TRANSFORMADA - Aplica DCT
								coefs = cv2.dct(sbimg)
								#QUANTIZAÇÃO/LIMIARIZAÇÃO
						
								zcoefs = np.round( coefs/Z[:,:,ch] )      #Coeficientes normalizados - ^T(u,v)=arred{T(u,v)/Z(u,v)}
#								print Z[:,:,ch],
								seq = h.zigzag(zcoefs)                     #Gera Sequencia de coeficientes 1-D
#								print seq,
								hfcd = hf.fwdhuff(DCant, seq, ch)          #Gera o codigo huffman da subimagem
#								print seq
								DCant = seq[0]
								self.NumBits += hfcd[0]
								seqhuff += hfcd[1]
						vec += 1
				#Salvar os codigos em arquivo
				#fo.write(seqhuff+'\n')
				outseq.append(seqhuff)
				seqhuff = ''
				
		elif self.mode == '420':
			if chnl == 1:
				Ymg = dYmg
			else:
				Y = dYmg[:,:,0]
				dims, CrCb = h.adjImg(downsample(dYmg[:,:,1:3], self.mode)[1])
				Ymg = [ Y, CrCb[:,:,0], CrCb[:,:,1] ]
				self.lYmg = Ymg
			for ch in range(chnl):
				vec = 0
				DCant = 0
				if ch == 0: #LUMINANCIA
					M = self.Madj #self.nBlkRows
					N = self.Nadj #self.nBlkCols
					m = self.mbr
					n = self.mbc
				else:       #CROMINANCIA
					#rBLK, cBLK = int(np.floor(dims[0]/self.mbr)), int(np.floor(dims[1]/self.mbc))
					M = int(np.floor(dims[0])) #int(np.floor(dims[0]/self.r)) #
					N = int(np.floor(dims[1])) #int(np.floor(dims[1]/self.c)) #
					m = self.r
					n = self.c
				
				for x in range(0, M, m):
					for y in range(0, N, n):
						#SELEÇAO DE TABELA
#						print len(self.MV)
#						print x, y, M, N, vec, len(self.MV), int(abs(self.MV[vec][0])), int(abs(self.MV[vec][1]))
						Z = self.Zhvs[ int(abs(self.MV[vec][0])) ][ int(abs(self.MV[vec][1])) ]
						vec += 1
						
						for i in range(x, x+m, self.r):
							for j in range(y, y+n, self.c):
								sbimg = Ymg[ch][i:i+r, j:j+c]     #Subimagens nxn
								#TRANSFORMADA - Aplica DCT
#								print sbimg.shape, ch
								coefs = cv2.dct(sbimg)
								#QUANTIZAÇÃO/LIMIARIZAÇÃO
#								print coefs.shape, Z.shape
								zcoefs = np.round_( coefs/Z[:,:,ch] )      #Coeficientes normalizados - ^T(u,v)=arred{T(u,v)/Z(u,v)}
								#CODIFICAÇÃO - Codigos de Huffman - FOWARD HUFF
								seq = h.zigzag(zcoefs)                     #Gera Sequencia de coeficientes 1-D
								hfcd = hf.fwdhuff(DCant, seq, ch)          #Gera o codigo huffman da subimagem
								DCant = seq[0]
								self.NumBits += hfcd[0]
								seqhuff += hfcd[1]
						
                #Salvar os codigos em arquivo
                #fo.write(seqhuff + '\n')
				outseq.append(seqhuff)
				seqhuff = ''
				
		#fo.close()
		self.avgBits = (float(self.NumBits)/float(self.M*self.N))
		self.CRate = 24./self.avgBits
		self.Redunc = 1.-(1./self.CRate)
		#print '- Encoder Complete...'
		#return (self.CRate, self.Redunc, self.NumBits)
		return outseq
		
		
	def Outcomes(self):
		'''
		'''
		
		print '    :: Taxa de Compressao: %2.3f'%(self.CRate)
		print '    :: Redundancia de Dados: %2.3f' %(self.Redunc)
		print '    :: Numero total de bits: ', self.NumBits
		print '    :: Media de bits/Pixel: %2.3f' %(self.avgBits)
#End class Encoder
        
class Decoder:
    '''
    '''
    
    def __init__(self, huffcode, hufftables, hvstables, args):  #filename):
        '''
        '''
        
        #self.fl = open(filename,'r')        #header = hdr #self.fl.readline().split(',')                  #Lê cabeçalho
        self.SHAPE, self.qually, self.mode, self.motionVec = args[0], args[1], args[2], args[3] #int(header[0]), int(header[1]), int(header[2]), int(header[3]), header[4][:-1]
        self.huffcodes = huffcode        #self.SHAPE = conf[0] #(self.Mo, self.No, self.Do)
        (self.M, self.N, self.D), self.imRaw = h.adjImg( np.zeros(self.SHAPE) )
        #NUMERO DE BLOCOS NA VERTICAL E HORIZONTAL
        self.R, self.C = [8,8]
        self.mbr, self.mbc = [16,16]
        #NUMERO DE BLOCOS NA VERTICAL E HORIZONTAL
        self.nBlkRows = int(np.floor(self.M/self.R))
        self.nBlkCols = int(np.floor(self.N/self.C))
        #Gera Tabela de Quantizaçao
        self.hvstables = hvstables
        self.hufftables = hufftables
        
        if self.D == 2:
            self.NCHNL = 1
        elif self.D == 3:
            self.NCHNL = 3

    def _run_(self):
        '''
        '''
        hf = h.HuffCoDec(self.hufftables)
        img = np.zeros((self.M,self.N,self.D), np.float32)
		
        if self.mode == '444':
            pass

        elif self.mode == '420':
            for ch in range (3):
                if ch == 0:
                    nblk, seqrec = hf.invhuff(self.huffcodes[ch], ch)
                    rBLK = self.nBlkRows
                    cBLK = self.nBlkCols
                    count = 0														
                    for x in range (0, self.M, self.mbr):
                        for y in range (0, self.N, self.mbc):
                            for a in range (x, x+self.mbr, self.R):
                                for b in range (y, y+self.mbc, self.C):
                                    img[a:a+self.R, b:b+self.C, ch] = h.zagzig(seqrec[(a/8)*cBLK + (b/8)])									
                                    
                    for x in range (0, self.M, self.mbr):
                        for y in range (0, self.N, self.mbc):
                            # Quantization table
                            if len(self.motionVec[count]) == 2:
                                Z = self.hvstables[abs(self.motionVec[count][0])][abs(self.motionVec[count][1])]
                            elif len(self.motionVec[count]) == 3:
                                Z = self.hvstables[abs(self.motionVec[count][1])][abs(self.motionVec[count][2])]
                            else:
                                Z = self.hvstables[int((abs(self.motionVec[count][1])+abs(self.motionVec[count][3]))/2.)][int((abs(self.motionVec[count][2])+abs(self.motionVec[count][4]))/2.)]
                            for i in range (x, x+self.mbr, self.R):
                                for j in range (y, y+self.mbc, self.C):
                                    img[i:i+self.R, j:j+self.C, ch] = np.round_(cv2.idct( img[i:i+self.R, j:j+self.C, ch]*Z[:,:,ch] ))
                            count += 1
                else:
                    nblk, seqrec = hf.invhuff(self.huffcodes[ch], ch)
                    rBLK = int(np.floor(self.M/self.mbr))
                    cBLK = int(np.floor(self.M/self.mbc))																				
                    count = 0
                    for x in range (rBLK):
                        for y in range (cBLK):
                            # Quantization table
                            if len(self.motionVec[count]) == 2:
                                Z = self.hvstables[abs(self.motionVec[count][0])][abs(self.motionVec[count][1])]
                            elif len(self.motionVec[count]) == 3:
                                Z = self.hvstables[abs(self.motionVec[count][1])][abs(self.motionVec[count][2])]
                            else:
                                Z = self.hvstables[int(np.floor((abs(self.motionVec[count][1])+abs(self.motionVec[count][3]))/2.))][int(np.floor((abs(self.motionVec[count][2])+abs(self.motionVec[count][4]))/2.))]										
                            img[x:x+self.mbr, y:y+self.mbc, ch] = upsample(np.round_(cv2.idct(h.zagzig(seqrec[x*cBLK + y])*Z[:,:,ch])), self.mode, 2)
                            count += 1
																												
        return img

#    def _run_(self):
#        '''
#        '''
#        #print '- Running Mjpeg Decoder...'
#        hf = h.HuffCoDec(self.hufftables)
#        r, c, chnl = self.R, self.C, self.NCHNL
#        
#        #hufcd = self.huffcodes#self.fl.readline()[:-1]
#        if self.mode == '444':
#            for ch in range(chnl):                #hufcd = self.fl.readline()[:-1]            #    print hufcd[0:20]
#                nblk, seqrec = hf.invhuff(self.huffcodes[ch], ch)
#                count = 0
#                for i in range(self.nBlkRows):
#                    for j in range(self.nBlkCols):
#                        if len(self.motionVec[count]) == 2:
#                                Z = self.hvstables[self.motionVec[count][0]][self.motionVec[count][1]]
#                        elif len(self.motionVec[count]) == 3:
#                                Z = self.hvstables[self.motionVec[count][1]][self.motionVec[count][2]]
#                        else:
#                                Z = self.hvstables[(self.motionVec[count][1]+self.motionVec[count][3])/2][(self.motionVec[count][2]+self.motionVec[count][4])/2]
#                        blk = h.zagzig(seqrec[i*self.nBlkCols + j])
#                        self.imRaw[r*i:r*i+r, c*j:c*j+c, ch] = np.round_( cv2.idct( blk*Z[:,:,ch] ))
##                        count += 1
#                        
#        elif self.mode == '420':
#            #import math as m
##            imrec = np.zeros((self.M, self.N, 3))
#        
#            if chnl == 1:
#                rYmg = self.imRaw
#            else:                #Y = self.imRaw[:,:,0]
#                Y = np.zeros( (self.M, self.N) )
#                dims, CrCb = h.adjImg( downsample(np.zeros( (self.M, self.N, 2) ), self.mode)[1] )
#                rYmg = [ Y, CrCb[:,:,0], CrCb[:,:,1] ]
#                
#            for ch in range(chnl):
#                #hufcd = self.fl.readline()[:-1]
#                if ch == 0:
#                    rBLK = self.nBlkRows
#                    cBLK = self.nBlkCols
#                    M, N = self.M, self.N
#                    m, n = self.mbr, self.mbc
#                else:
#                    rBLK, cBLK = int(np.floor(dims[0])), int(np.floor(dims[1]))
#                    M, N = dims[0], dims[1]
#                    m, n = self.R, self.C
##                    print 'Crominance OK'
##                print 'Ok!!!!'
#                nblk, self.seqrec = hf.invhuff(self.huffcodes[ch], ch)
#                
#                count = 0
#                ind = 0
#                for x in range(0, M, m):
#                    for y in range(0, N, n):
##                        
##                        print self.motionVec[count], ch, count, ind
##                        print '   ', M, N, m, n, x, y, self.nBlkRows, self.nBlkCols
##                        
#                        if self.motionVec[count][0] == 'b' or self.motionVec[count][0] == 'f':
#                            Z = self.hvstables[self.motionVec[count][1]][self.motionVec[count][2]]
#                        elif self.motionVec[count][0] == 'i':
#                            Z = self.hvstables[np.floor((self.motionVec[count][1]+self.motionVec[count][3])/2.)][np.floor((self.motionVec[count][2]+self.motionVec[count][4])/2.)]
##                            Z = self.hvstables[self.motionVec[count][1]][self.motionVec[count][2]]
#                        else:
#                            Z = self.hvstables[self.motionVec[count][0]][self.motionVec[count][1]]
#                            
#                        count += 1
##                        
#                        for i in range(x, x+m, self.R):
#                            for j in range(y, y+n, self.C):
#                                blk = h.zagzig(self.seqrec[ind])
#                                ind += 1
#                                rYmg[ch][m*i:m*i+self.R, n*j:n*j+self.C] = np.round_( cv2.idct( blk*Z[:,:,ch] ))
#                
##                self.imRaw[:,:,0] = rYmg[0]
##                self.imRaw[:,:,1] = upsample(self.imRaw[:,:,1], self.mode, 2)
##                self.imRaw[:,:,2] = upsample(self.imRaw[:,:,2], self.mode, 2)
#                
#                
##                print nblk, len(self.seqrec), ch
##                for i in range(rBLK):
##                    for j in range(cBLK):
###                        print rBLK, cBLK, i, j, dims[0], dims[1]
##                        blk = h.zagzig(self.seqrec[i*cBLK + j])
##                        rYmg[ch][r*i:r*i+r, c*j:c*j+c] =  blk
##                        rYmg[ch][r*i:r*i+r, c*j:c*j+c] = np.round_( cv2.idct( blk*Z[:,:,ch] ))
#
#            # UPSAMPLE 1
#                if ch == 0:
#                    self.imRaw[:,:,0] = rYmg[0]       #                    self.imRaw = rYmg
##                    imrec[:,:,0] = rYmg[0]
#                else:
##                    self.imRaw[:,:,ch] = upsample(rYmg[ch], self.mode, 1) #[:self.M, :self.N]
#                    self.imRaw[:,:,1] = upsample(rYmg[ch], self.mode, 2)
#                    self.imRaw[:,:,2] = upsample(rYmg[ch], self.mode, 2)
#                    
##            print self.imRaw[:,:,1]
#
#            # to be continued...
#            count = 0
#            for i in range (0, self.nBlkRows, 2):
#                for j in range (0, self.nBlkCols, 2):
#                    if i%16 == 0 and j%16 == 0:
#                        if len(self.motionVec[count]) == 2:
#                            Z = self.hvstables[self.motionVec[count][0]][self.motionVec[count][1]]
#                        elif len(self.motionVec[count]) == 3:
#                            Z = self.hvstables[self.motionVec[count][1]][self.motionVec[count][2]]
#                        else:
#                           Z = self.hvstables[(self.motionVec[count][1]+self.motionVec[count][3])/2][(self.motionVec[count][2]+self.motionVec[count][4])/2]
#                    blk = self.imRaw[r*i:r*i+r, c*j:c*j+c, ch]
#                    self.imRaw[r*i:r*i+r, c*j:c*j+c, ch] = np.round_( cv2.idct( blk*Z[:,:,ch] ))
#                    blk = self.imRaw[r*i+r:r*i+(2*r), c*j:c*j+c, ch]
#                    self.imRaw[r*i+r:r*i+(2*r), c*j:c*j+c, ch] = np.round_( cv2.idct( blk*Z[:,:,ch] ))
#                    blk = self.imRaw[r*i:r*i+r, c*j+c:c*j+(2*c), ch]
#                    self.imRaw[r*i:r*i+r, c*j+c:c*j+(2*c), ch] = np.round_( cv2.idct( blk*Z[:,:,ch] ))
#                    blk = self.imRaw[r*i+r:r*i+(2*r), c*j+c:c*j+(2*c), ch]
#                    self.imRaw[r*i+r:r*i+(2*r), c*j+c:c*j+(2*c), ch] = np.round_( cv2.idct( blk*Z[:,:,ch] ))
#                    count += 1
#        #UPSAMPLE 2
##        self.imRaw[:,:,1] = upsample(self.imRaw[:,:,1], self.mode, 2)
##        self.imRaw[:,:,2] = upsample(self.imRaw[:,:,2], self.mode, 2)
##        imrec = self.imRaw #+ 128.0
##        print self.imRaw[:,:,1]
#        
#        return self.imRaw #imrec
#
#                            ind += 1

def downsample(mat, mode):
    '''
    '''
        
    import math as m
    M, N, D = mat.shape
    #M, N = mat.shape
    #D = mat[0,0].shape[0]
    ndims = ( m.ceil(M/2), m.ceil(N/2) )
    newmat = np.zeros((ndims[0], ndims[1], D))
    #aux = np.zeros((m.ceil(M/2), N, D))
    
    if mode == '420':
        newmat = mat[::2,::2]
    elif mode == '422':
        pass
        
    #dims, newmat = h.adjImg(newmat)
    return ndims, newmat
    #return h.adjImg(newmat)

def upsample(mat, mode, uptype):
    '''
    '''
    
    M, N = mat.shape
    
    if uptype == 1:
        newmat = np.zeros((M*2, N*2))
        if mode == '420':
            newmat[::2, ::2] = mat
        elif mode == '422':
            pass
    elif uptype == 2:
        newmat = np.zeros((2*M, 2*N))
        if mode == '420':
            newmat[::2, ::2] = mat
            newmat[::2, 1::2] = newmat[::2,::2]
            newmat[1::2, :] = newmat[::2, :]
        elif mode == '422':
            pass
    
    return newmat
    
    