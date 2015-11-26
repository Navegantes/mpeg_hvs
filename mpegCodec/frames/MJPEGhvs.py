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
#                    for i in range (self.nBlkRows):
#                        for j in range (self.nBlkCols):
#                            img[self.R*i:self.R*i+self.R, self.C*j:self.C*j+self.C, ch] = h.zagzig(seqrec[i*self.nBlkCols + j])
                                    
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
    
    