import functools

class alias_dict(dict): #will only work with strings as keys and is case insensetive
    def __init__(self,*args,**kwargs):
        dict.__init__(self,*args,**kwargs)
        self.aliases = dict()
    def get_key(self,alias):
        return self.aliases.get(alias,alias)

    def __getitem__(self,key):
        key = key.lower()
        return dict.__getitem__(self ,self.get_key(key))

    def __setitem__(self,key,value):
        key = key.lower()
        return dict.__setitem__(self,self.get_key(key),value)

    def __contains__(self,key):
        key = key.lower()
        return dict.__contains__(self,self.get_key(key))
    
    def pop(self,key,*args,**kwargs):
        key = key.lower()
        return dict.pop(self,self.get_key(key),*args,**kwargs)
    
    def add_alias (self,key,alias):
        key = key.lower()
        alias = alias.lower()
        self.aliases[alias] = key
    
    def add_aliases(self,key,aliases):
        for alias in aliases:
            self.add_alias(key,alias)

    def add_aliases_from_dict(self,dic):
        for key in dic:
            self.add_aliases(key,dic[key])
    
    def __delitem__(self,key):
        key = key.lower()
        print("deleting",key)
        for i in self.aliases:
            if self.aliases[i] ==key:
                self.aliases.pop(i)
        return dict.__delitem__(self,self.get_key(key))

    def del_alias(self,alias):
        alias = alias.lower()
        return self.aliases.pop(alias)

    def rename_key(self,old_key, new_key):
        old_key = old_key.lower()
        new_key = new_key.lower()
        self.__setitem__(new_key,self.pop(self.get_key(old_key)))
        for i in self.aliases:
            if self.aliases[i] ==old_key:
                self.aliases[i] = new_key
                dict.value
    
    def rename_alias(self,old_alias,new_alias):
        self.alias[new_alias] = self.alias.pop(old_alias)
    def keys (self):
        return list(dict.keys(self)) + list(self.aliases.keys())

class callable_dict():
    def __init__(self):
        self.cmds = alias_dict()
        class user_callable_command():
            def __init__(inner_self,func,*args,**kwargs):
                inner_self.func = func
                inner_self.args = args
                inner_self.kwargs = kwargs
                inner_self.name = inner_self.func.__name__
                if "name" in inner_self.kwargs:
                    inner_self.name = inner_self.kwargs["name"]
                self.cmds[inner_self.name]=inner_self
                if "alias" in inner_self.kwargs:
                    self.cmds.add_alias(inner_self.name, kwargs["alias"])
                if 'aliases' in inner_self.kwargs:
                    self.cmds.add_aliases(inner_self.name,kwargs['aliases'])
                functools.update_wrapper(inner_self, func)
            def __call__(inner_self,*fargs,**fkwargs):
                return(inner_self.func(*fargs,**fkwargs))  
        self._base_class =user_callable_command 
    def add(self,*args,**kwargs):# this is wrapper classes, just dont think about it too hard
        def wrapper(func):
            class user_callable_commandsp(self._base_class):
                @functools.wraps(func)
                def __call__(self,*fargs,**fkwargs):
                    return(self.func(*fargs,**fkwargs))
            return user_callable_commandsp(func,*args,**kwargs)
        return wrapper