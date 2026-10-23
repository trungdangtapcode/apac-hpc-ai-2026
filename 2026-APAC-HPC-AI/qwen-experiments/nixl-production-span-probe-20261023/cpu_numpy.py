"""Small deterministic array subset for executing pinned methods without NumPy installed."""

class Array:
    def __init__(self, data, ndim=1):
        if isinstance(data, Array): data=data.data
        self.data=data; self.ndim=ndim
    def __len__(self): return len(self.data)
    def __iter__(self): return iter(self.data)
    def tolist(self): return [list(x) if isinstance(x,list) else x for x in self.data]
    def astype(self, dtype): return Array(self.data,self.ndim)
    def ravel(self):
        if self.ndim==1:return Array(list(self.data))
        return Array([v for row in self.data for v in row])
    def _vec(self, other, op):
        if isinstance(other,Array):
            if self.ndim==other.ndim==1:
                if len(self)!=len(other): raise ValueError('vector length mismatch')
                return Array([op(a,b) for a,b in zip(self.data,other.data)])
            if self.ndim==other.ndim==2:
                rows=max(len(self.data),len(other.data)); cols=max(len(self.data[0]),len(other.data[0]))
                out=[]
                for i in range(rows):
                    row=[]
                    for j in range(cols): row.append(op(self.data[i if len(self.data)>1 else 0][j if len(self.data[i if len(self.data)>1 else 0])>1 else 0],other.data[i if len(other.data)>1 else 0][j if len(other.data[i if len(other.data)>1 else 0])>1 else 0]))
                    out.append(row)
                return Array(out,2)
            if self.ndim==2 and other.ndim==1:
                return Array([[op(v,other.data[j]) for j,v in enumerate(row)] for row in self.data],2)
            if self.ndim==1 and other.ndim==2:
                return Array([[op(self.data[j],v) for j,v in enumerate(row)] for row in other.data],2)
        if self.ndim==2: return Array([[op(v,other) for v in row] for row in self.data],2)
        return Array([op(v,other) for v in self.data])
    def __add__(self,x): return self._vec(x,lambda a,b:a+b)
    def __radd__(self,x): return self.__add__(x)
    def __sub__(self,x): return self._vec(x,lambda a,b:a-b)
    def __mul__(self,x): return self._vec(x,lambda a,b:a*b)
    def __ne__(self,x): return self._vec(x,lambda a,b:a!=b)
    def __or__(self,x): return self._vec(x,lambda a,b:bool(a) or bool(b))
    def __getitem__(self,key):
        if isinstance(key,tuple):
            if key==(slice(None),None): return Array([[x] for x in self.data],2)
            if key==(None,slice(None)): return Array([list(self.data)],2)
            raise IndexError(key)
        if isinstance(key,slice): return Array(self.data[key],self.ndim)
        if isinstance(key,Array): return Array([self.data[i] for i in key.data],self.ndim)
        if isinstance(key,list): return Array([self.data[i] for i in key],self.ndim)
        return self.data[key]
    def __setitem__(self,key,value):
        if isinstance(key,slice):
            values=value.data if isinstance(value,Array) else list(value)
            self.data[key]=values
        else:self.data[key]=value

class MiniNP:
    uint64=int
    int64=int
    int32=int
    bool=bool
    @staticmethod
    def asarray(v,dtype=None): return v if isinstance(v,Array) else Array(list(v))
    @staticmethod
    def array(v,dtype=None): return MiniNP.asarray(v,dtype)
    @staticmethod
    def arange(n,dtype=None): return Array(list(range(int(n))))
    @staticmethod
    def full(n,value,dtype=None): return Array([value]*int(n))
    @staticmethod
    def ones(n,dtype=None): return Array([True]*int(n))
    @staticmethod
    def full_like(a,value,dtype=None): return Array([value]*len(a))
    @staticmethod
    def flatnonzero(a): return Array([i for i,v in enumerate(a) if v])
    @staticmethod
    def concatenate(parts): return Array([v for p in parts for v in (p.data if isinstance(p,Array) else p)])
    @staticmethod
    def tile(a,n): return Array((a.data if isinstance(a,Array) else list(a))*int(n))
    @staticmethod
    def column_stack(parts):
        cols=[p.data if isinstance(p,Array) else list(p) for p in parts]
        return Array([list(row) for row in zip(*cols)],2)

np=MiniNP()
