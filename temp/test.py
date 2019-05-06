
# sudo apt-get install graphviz

from graphviz import Source, render

src = Source('''digraph G {node[shape=record];
			  "0x00124b001936db2f" [style="bold", label="{0x00124b001936db2f|Coordinator|No model information available|online}"];
			  "0x00124b001936db2f" -> "0x0017880104878b88" [label="215"]
			  "0x00124b001936db2f" -> "0x00178801040c9476" [label="250"]
			  "0x0017880104878b88" [style="rounded", label="{Deckenlampe_01|Router|Philips Hue white and color ambiance E26/E27/E14 (9290012573A)|online}"];
			  "0x0017880104878b88" -> "0x00124b001936db2f" [label="73"]
			  "0x0017880104878b88" -> "0x00178801040c9476" [label="252"]
			  "0x00178801040c9476" [style="rounded", label="{Deckenlampe_02|Router|Philips Hue white and color ambiance E26/E27/E14 (9290012573A)|online}"];
			  "0x00178801040c9476" -> "0x00124b001936db2f" [label="83"]
			  "0x00178801040c9476" -> "0x0017880104878b88" [label="255"]
			}''')


src.render(filename='zigbee_diagram', format='png', cleanup=True)
