mkdir -p ocr_pdf
mkdir -p ocr_txt
mkdir -p pdf_orig
for i in *.pdf; do
	type="$(file -b $i)"
	if [ "${type%%,*}" == "PDF document"  ]; 
	then
		mkdir "${i%.*}"
		convert -density 300 -deskew 40 -colorspace gray -threshold 70% "$i" "${i%.*}"/"${i%.*}".png
		for p in "${i%.*}"/*.png; do
			tesseract -l hrv -psm 1 "${p%.*}".png "${p%.*}"
			tesseract -l hrv -psm 1 "${p%.*}".png "${p%.*}" pdf
		done
		cat "${i%.*}"/*.txt > ocr_txt/"${i%.*}".txt
		mv "$i" pdf_orig/"$i"
		pdfunite $(ls -v ${i%.*}/*.pdf) ocr_pdf/"${i%.*}".pdf
		rm -rf "${i%.*}"
	else
		echo "Nema pdf-ova za OCR"
	fi
done
