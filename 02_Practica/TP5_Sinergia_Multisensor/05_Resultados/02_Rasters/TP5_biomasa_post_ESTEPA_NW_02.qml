<!DOCTYPE qgis><qgis version="3.34" styleCategories="Symbology">
  <!-- Biomasa aérea estimada (Mg/ha)
       ADVERTENCIA: el modelo de altura subestima los arboles altos (sesgo medido
       de casi 10 m por encima de 15 m) y la alometria lo amplifica. Este mapa
       SUBESTIMA los rodales altos. Ver TP5_03 y TP5_04. -->
  <pipe><rasterrenderer type="singlebandpseudocolor" band="1" opacity="1">
    <rastershader><colorrampshader classificationMode="1" colorRampType="INTERPOLATED">
      <item value="0" color="#ffffe5" label="0"/>
      <item value="25" color="#fee391" label="25"/>
      <item value="75" color="#fe9929" label="75"/>
      <item value="150" color="#993404" label="150"/>
    </colorrampshader></rastershader>
  </rasterrenderer></pipe>
</qgis>
