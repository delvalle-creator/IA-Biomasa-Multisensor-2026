<!DOCTYPE qgis>
<qgis version="3.28" styleCategories="Symbology">
  <renderer-v2 type="graduatedSymbol" attr="diferencia_m" graduatedMethod="GraduatedColor">
    <ranges>
      <range lower="-100" upper="-5" label="ATL08 mas bajo (menos de -5 m)" symbol="0"/>
      <range lower="-5" upper="-2" label="-5 a -2 m" symbol="1"/>
      <range lower="-2" upper="2" label="-2 a 2 m (coinciden)" symbol="2"/>
      <range lower="2" upper="5" label="2 a 5 m" symbol="3"/>
      <range lower="5" upper="100" label="ATL08 mas alto (mas de 5 m)" symbol="4"/>
    </ranges>
    <symbols>
      <symbol type="fill" name="0"><layer class="SimpleFill">
        <prop k="color" v="5,113,176,180"/><prop k="outline_color" v="120,120,120,255"/></layer></symbol>
      <symbol type="fill" name="1"><layer class="SimpleFill">
        <prop k="color" v="146,197,222,180"/><prop k="outline_color" v="120,120,120,255"/></layer></symbol>
      <symbol type="fill" name="2"><layer class="SimpleFill">
        <prop k="color" v="245,245,245,180"/><prop k="outline_color" v="120,120,120,255"/></layer></symbol>
      <symbol type="fill" name="3"><layer class="SimpleFill">
        <prop k="color" v="244,165,130,180"/><prop k="outline_color" v="120,120,120,255"/></layer></symbol>
      <symbol type="fill" name="4"><layer class="SimpleFill">
        <prop k="color" v="202,0,32,180"/><prop k="outline_color" v="120,120,120,255"/></layer></symbol>
    </symbols>
  </renderer-v2>
</qgis>
