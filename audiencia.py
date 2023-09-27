from typing import Hashable, Sequence
from collections import Counter
from functools import reduce
from itertools import combinations, chain, product
from operator import add
import pandas as pd
import json

class Audiencia:
    def __init__(self, nome: str, dados: Sequence[Hashable]) -> None:
        self.__nome = nome
        self.__tipo = self.__validar_tipos(nome, dados)
        self.__dados = Counter(dados)
        self.__origem:list["Audiencia"|None] = list()


    def __validar_tipos(self, nome, dados) -> str:
        if not isinstance(dados, Sequence):
            raise TypeError("As audiencia precisa ser uma sequencia.")
        
        elif len(dados) == 0:
            raise ValueError("A audiencia não pode estar vazia.")
        
        elif not isinstance(nome, str):
            raise ValueError("O nome da audiencia precisa ser um string.")
        
        elif len(nome) == 0:
            raise ValueError(
                "O nome da audiencia nao pode ser uma string vazia.")

        tipos = list(set(type(item) for item in dados))
        hasheavel = all([ isinstance(x, Hashable) for x in dados ])

        if len(tipos) > 1:
            raise TypeError("A audiencia contém itens de tipos diferentes.")
        
        if not hasheavel:
            raise TypeError("Os elementos da audiência precisam ser hasheaveis")
        
        return tipos[0]

    @property
    def multiconjunto(self):
        return self.__dados

    @property
    def nome(self):
        return self.__nome
    
    @property
    def tipo(self):
        return self.__tipo

    @property
    def elementos(self):
        return list(self.__dados.elements())
     
    @property
    def distintos(self):
        return set(self.__dados.keys())
    
    @property
    def origem(self):
        return self.__origem

    @property
    def interserccao_origens(self):
        distintos_das_origens = [a.distintos for a in self.__origem]
        if not distintos_das_origens:
            return {}
        else:
            return reduce(lambda x,y: x.intersection(y) ,[a.distintos for a in self.__origem] )
      

    def __hash__(self):
        return hash(self.nome)

    def __eq__(self, other):
        if isinstance(other, Audiencia):
            return self.nome == other.nome
        return False

    def __repr__(self):
        return f"Audiencia({self.__nome}, {len(self.distintos)}/{len(self.elementos)})"
    
    def __add__(self, other: "Audiencia") -> "Audiencia":
        if not isinstance(other, Audiencia):
            raise TypeError("Esta operações só pode ser feita entre audiencias")

        novo_nome = f"{self.nome}_{other.nome}"
        nova_audiencia = self.elementos + other.elementos
        nova_instancia = Audiencia(novo_nome, nova_audiencia)
        nova_instancia.__adcionar_origem(self)
        nova_instancia.__adcionar_origem(other)
        return nova_instancia
    
    def __adcionar_origem(self, original: "Audiencia") -> None:
        if isinstance(original, Audiencia):
            if len(original.origem) == 0:
                self.__origem.append(original)
            else:
                self.__origem.extend(original.origem)

    def comparador(self, comparavel:"Audiencia", com_elementos:bool=False):
        if isinstance(comparavel, Audiencia):
            if com_elementos:
                return {
                    'NOME' : self.nome,
                    'ELEMENTOS': self.elementos,
                    'ELEMENTOS_DISTINTOS' : self.distintos,
                    'COMPARADO_COM' : comparavel.nome,
                    'ELEMENTOS_COMPARAVEL': comparavel.elementos,
                    'ELEMENTOS_DISTINTOS_COMPARAVEL': comparavel.distintos,
                    'QUANTIDADE_INTERSECCAO_DAS_ORIGENS_COMPARAVEL': comparavel.interserccao_origens,
                    'INTERSECCAO_NAO_DISTINTA' :list(Counter({item:self.multiconjunto[item] for item in comparavel.multiconjunto.keys()}).elements()), 
                    'INTERSECCAO_DISTINTA': self.distintos.intersection(comparavel.distintos),
                    'DIFERENCA_NAO_DISTINTA': list((self.multiconjunto - comparavel.multiconjunto).elements()),
                    'DIFERENCA_DISTINTA' : self.distintos.difference(comparavel.distintos),
                    'INTERSECCAO_COM_INTERSECCAO_DAS_ORIGENS' :self.distintos.intersection(comparavel.interserccao_origens),

                }

            else:
                return {
                    'NOME' : self.nome,
                    'ELEMENTOS': len(self.elementos),
                    'ELEMENTOS_DISTINTOS' : len(self.distintos),
                    'COMPARADO_COM' : comparavel.nome,
                    'ELEMENTOS_COMPARAVEL': len(comparavel.elementos),
                    'ELEMENTOS_DISTINTOS_COMPARAVEL': len(comparavel.distintos),
                    'QUANTIDADE_INTERSECCAO_DAS_ORIGENS_COMPARAVEL': len(comparavel.interserccao_origens),
                    'INTERSECCAO_NAO_DISTINTA' : sum(self.multiconjunto[item] for item in comparavel.multiconjunto.keys()),
                    'INTERSECCAO_DISTINTA': len(self.distintos.intersection(comparavel.distintos)),
                    'DIFERENCA_NAO_DISTINTA': sum((self.multiconjunto - comparavel.multiconjunto).values()),
                    'DIFERENCA_DISTINTA' : len(self.distintos.difference(comparavel.distintos)),
                    'INTERSECCAO_COM_INTERSECCAO_DAS_ORIGENS' :len(self.distintos.intersection(comparavel.interserccao_origens)),

                }


class Interseccoes:
    def __init__(self, dados : dict[str, Sequence[Hashable]]) -> None:
        self.__validar_tipos(dados=dados)
        self.__audiencias = [ Audiencia(nome, audiencia) for nome, audiencia in dados.items() ]


    def __validar_tipos(self, dados:dict[str, Sequence[Hashable]]):
        if not isinstance(dados, dict):
            TypeError('dados precisa ser um dict')
        elif not all([ isinstance(chave, str) for chave in dados.keys()]):
            TypeError('Todas as chaves do dicionario "dados" precisam ser string')
        
    def __dados(self):
        combinacoes_de_audiencias = []
        qunatiade_audiencias = len(self.__audiencias)
        
        for tamanho_combinacoes in range(1, qunatiade_audiencias+1):
            combinacoes_de_audiencias.append(combinations(self.__audiencias, tamanho_combinacoes))

        combinacoes_de_audiencias = list(chain.from_iterable(combinacoes_de_audiencias))

        possiveis_combinacoes = []
        for combinacao in combinacoes_de_audiencias:
            if len(combinacao) == 1:
                possiveis_combinacoes.append(combinacao[0])
            else:
                combincao_somada = reduce(add, combinacao)
                possiveis_combinacoes.append(combincao_somada)

        combinacoes_finais = list(product(self.__audiencias, possiveis_combinacoes))

        base = [ de.comparador(para) for de, para in combinacoes_finais if de != para ]
        return base

    @property
    def dados_dicionario(self):
        return self.__dados()
    
    @property
    def dados_dataframe(self):
        return pd.DataFrame(self.__dados())
    
    @property
    def dados_json(self):
        return json.dumps(self.__dados())

